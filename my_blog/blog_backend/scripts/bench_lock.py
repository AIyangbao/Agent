#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bench_lock.py —— add 接口 Redis 分布式锁「真实并发」压测

⚠️ 铁律：本脚本必须放 tests/ 之外。tests/conftest.py 的 autouse fixture 会把
   RedisLockCtx 旁路成 no-op —— 在 tests/ 里跑的"并发"全是假并发。
   （这正是 2026-09-22 之前这把锁从未被真实验证过的原因。）

前置（三个终端，命令都在 blog_backend 下）：
  1) cd F:\\Agent\\my_blog && docker compose up -d mysql redis
  2) .\\venv\\Scripts\\python -m uvicorn main:app --host 0.0.0.0 --port 8000
  3) .\\venv\\Scripts\\python scripts\\bench_lock.py --user 账号 --password 密码
     （可选：--user2/--password2 跑双用户场景）

场景：
  S1  单用户串行 3 次    → 期望全部 200（锁能正常获取与释放，不是"发一次锁死10s"）
  S2  单用户并发 N 次    → 看「429 耗时指纹」+「数据面核对」（判定见 s2_same_user）
  S3  双用户并发（可选） → 期望两个用户都全部 200（锁按 user_id 隔离，不互相挡）
  S4  list_blogs 压测    → 缓存命中 QPS（响应 message 带"(缓存)"字样可观测）

压测产生的文章会在结束时自动软删（DELETE /api/blogs/delete）。
注意：每篇成功文章会触发一次真实的 RAG 后台 embedding（DashScope），量小可忽略。
"""

import argparse
import asyncio
import random
import statistics
import sys
import time

import httpx

# ---------------------------------------------------------------- 基础封装


def parse_args():
    p = argparse.ArgumentParser(description="add 接口分布式锁压测")
    p.add_argument("--base-url", default="http://127.0.0.1:8000")
    p.add_argument("--user", required=True, help="压测账号（会被频繁 add，建议用小号）")
    p.add_argument("--password", required=True)
    p.add_argument("--user2", default="", help="第二账号（可选，跑 S3 锁粒度场景）")
    p.add_argument("--password2", default="")
    p.add_argument("-n", "--concurrency", type=int, default=20, help="S2 并发数")
    p.add_argument("--qps-n", type=int, default=60, help="S4 总请求数")
    p.add_argument("--redis-url", default="redis://127.0.0.1:6379/0",
                   help="S2 独占探针用：本脚本自己占锁，测【纯拒绝耗时】。"
                        "本地跑容器栈时是 127.0.0.1:6379（override 暴露的端口）")
    p.add_argument("--no-probe", action="store_true", help="跳过 S2 的独占探针")
    return p.parse_args()


def make_title() -> str:
    ts = time.strftime("%Y%m%d%H%M%S")
    return f"压测{ts}{random.randint(100, 999)}"


async def login(client: httpx.AsyncClient, base: str, username: str, password: str) -> str:
    """登录拿 JWT。注意：密码连续错 5 次会触发防爆破锁定 10 分钟，别乱试。"""
    r = await client.post(f"{base}/api/user/login",
                          json={"username": username, "password": password})
    r.raise_for_status()
    body = r.json()
    if body.get("code") != 200:
        sys.exit(f"登录失败：{body}")
    return body["data"]["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def get_my_id(client, base, token) -> int | None:
    """取当前用户 id —— 用来拼出 Redis 里的锁 key（lock:add_blog:<uid>）。"""
    r = await client.get(f"{base}/api/user/me", headers=auth_header(token))
    try:
        return r.json()["data"]["id"]
    except Exception:
        return None


async def hold_lock_probe(client, base, token, uid, redis_url) -> int | None:
    """独占探针：脚本自己往 Redis 里占住锁，然后只发 1 个 add。

    价值：这个 429 的耗时里**没有任何并发/排队**，是纯粹的"拒绝路径耗时"。
      ≈ 裸成本(几 ms~20ms)  → 拒绝是立即返回的，fail-fast 生效
      多出 ~100/200/300ms  → 拒绝路径里在 await sleep(retry_delay)，
                             即运行环境里的 retry 不是 1
    """
    if uid is None:
        print("  ⚠️ 跳过独占探针：没拿到 user id")
        return None
    try:
        import redis.asyncio as aioredis
    except ImportError:
        print("  ⚠️ 跳过独占探针：venv 里没有 redis 包")
        return None

    key = f"lock:add_blog:{uid}"
    r = aioredis.from_url(redis_url, decode_responses=True, socket_timeout=2)
    try:
        await r.set(key, "bench-probe", ex=30)
        status, body, lat = await timed_add(client, base, token, make_title())
        new_id = (body.get("data") or {}).get("id") if isinstance(body, dict) else None
        verdict = ("拒绝立即返回（无 sleep）" if lat < 60
                   else f"拒绝路径里有额外等待 ≈{lat - 10:.0f}ms")
        print(f"  ① 独占探针（无并发）：{status}  {lat:.0f}ms　→ {verdict}")
        if status != 429:
            print("     ⚠️ 探针没被拒？说明锁 key 对不上（uid 或 key 前缀），结果不可信")
        return status, lat, (new_id if status == 200 else None)
    except Exception as e:
        print(f"  ⚠️ 跳过独占探针：{e!r}（检查 {redis_url} 是否可达）")
        return None, None, None
    finally:
        try:
            await r.delete(key)
            await r.aclose()
        except Exception:
            pass


async def add_blog(client, base, token, title) -> tuple[int, dict]:
    r = await client.post(f"{base}/api/blogs/add",
                          headers=auth_header(token),
                          json={"title": title, "content": f"{title} 压测正文"})
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {}


async def delete_blog(client, base, token, blog_id):
    r = await client.delete(f"{base}/api/blogs/delete",
                            headers=auth_header(token), params={"id": blog_id})
    return r.status_code


async def count_by_keyword(client, base, keyword) -> int:
    """用列表接口的 keyword 搜索核对库里实际落了几篇（数据面验证，不只看状态码）。"""
    r = await client.get(f"{base}/api/blogs/list_blogs",
                         params={"keyword": keyword, "page": 1, "pageSize": 100})
    body = r.json()
    return body["data"]["total"]


async def timed_add(client, base, token, title):
    """带耗时的 add。

    429 的耗时是判断「服务端到底跑的是 retry=1 还是 retry=3」的关键指纹：
      - fail-fast（retry=1）：抢不到立刻返回，429 耗时 ~1ms（秒回）
      - retry=3 + retry_delay=0.1：至少睡 2 轮，429 耗时 ≥200ms
    """
    t0 = time.perf_counter()
    try:
        status, body = await add_blog(client, base, token, title)
    except Exception as e:
        return 500, {"detail": repr(e)}, (time.perf_counter() - t0) * 1000
    return status, body, (time.perf_counter() - t0) * 1000


def pct(vals, q) -> float:
    """极简分位数（vals 为空返回 0）。"""
    if not vals:
        return 0.0
    vals = sorted(vals)
    return vals[min(len(vals) - 1, int(len(vals) * q))]


def fmt_results(results) -> dict:
    """把 [(status, body), ...] 汇总成 {状态码: 个数}"""
    dist: dict[int, int] = {}
    for status, _ in results:
        dist[status] = dist.get(status, 0) + 1
    return dict(sorted(dist.items()))


# ---------------------------------------------------------------- 场景


async def s1_serial(client, base, token, n=3):
    """S1 串行：锁的"健康检查"——能拿也能放。"""
    print(f"\n[S1] 单用户串行 x{n}（锁正常获取/释放）")
    ok = 0
    for i in range(n):
        t0 = time.perf_counter()
        status, body = await add_blog(client, base, token, make_title())
        cost = (time.perf_counter() - t0) * 1000
        ok += status == 200
        print(f"  #{i + 1} {status}  {cost:.0f}ms")
        if status == 200:
            s1_ids.append(body["data"]["id"])
    verdict = "✅ PASS" if ok == n else "❌ FAIL（锁可能没释放/误伤正常请求）"
    print(f"  结果：{ok}/{n} 成功 → {verdict}")
    return ok == n


s1_ids: list[int] = []


async def me_latencies(client, base, token, n) -> list[float]:
    """对照组：并发打 /api/user/me（含 JWT 校验 + 1 次 DB 查询，完全不碰锁）。

    作用：量化「这个并发度下每个请求的裸成本」。被拒请求的耗时要跟它比，
    而不是跟 0 比 —— 否则会把 DB / 事件循环的争用延迟误判成「锁在重试」。
    """
    async def one():
        t0 = time.perf_counter()
        await client.get(f"{base}/api/user/me", headers=auth_header(token))
        return (time.perf_counter() - t0) * 1000

    return list(await asyncio.gather(*[one() for _ in range(n)]))


async def s2_same_user(client, base, token, n, uid=None, redis_url="redis://127.0.0.1:6379/0",
                       no_probe=False):
    """S2 同用户并发：核心场景（互斥 + 防重复提交）。

    三层证据，从干净到嘈杂：
      ⓪ 对照组  /api/user/me x10 → 并发下"裸成本"基线（鉴权 + DB，不含锁）
      ① 指纹    add x3 并发     → 被拒的那个 429 等了多久
                                 fail-fast（retry=1）：429 ≈ 裸成本，额外等待 ≈ 0
                                 还在重试（retry=3）：会多出 retry×retry_delay ≈ 300ms
      ② 主场景  add xN 并发     → 状态码分布 / 耗时 / 数据面核对

    ⚠️ 判定只看两件事：**429 的额外等待是否≈0** + **库里篇数是否 == 成功数**。
       成功数不要求等于 1：请求到达本身有 stagger（毫秒级），临界区又只有十几毫秒，
       后来者落在锁的空闲窗口里"合法"进入是正常的，不等于锁失效。
    """
    print(f"\n[S2] 同用户并发 x{n}（核心场景：互斥 + 防重复提交）")
    title_prefix = make_title()

    # ⓪ 对照组：并发下的裸成本
    me_lat = await me_latencies(client, base, token, 10)
    base_cost = pct(me_lat, 0.5)
    print(f"  ⓪ 对照 /api/user/me x10：p50={base_cost:.0f}ms max={max(me_lat):.0f}ms"
          f"　← 429 的耗时要跟它比，不是跟 0 比")

    # ① 独占探针：自己占住锁再发 1 个请求 → 没有并发干扰的"纯拒绝耗时"
    probe_status, probe_lat = None, None
    ok_ids_probe: list[int] = []
    if not no_probe:
        probe_status, probe_lat, probe_id = await hold_lock_probe(
            client, base, token, uid, redis_url)
        if probe_id:
            ok_ids_probe = [probe_id]

    # ② 指纹：3 并发，几乎没有争用
    fp = await asyncio.gather(
        *[timed_add(client, base, token, f"{title_prefix}_fp{i}") for i in range(3)])
    ok_ids: list[int] = ok_ids_probe + [b["data"]["id"] for s, b, _ in fp
                                        if s == 200 and isinstance(b, dict) and b.get("data")]
    fp_429 = [lat for s, _, lat in fp if s == 429]
    print("  ② 指纹 add x3：" + "　".join(f"{s} {lat:.0f}ms" for s, _, lat in fp))
    extra = (min(fp_429) - base_cost) if fp_429 else None
    if extra is None:
        print("     ⚠️ 3 并发没出现 429（到达太分散），指纹不可用，以主场景为准")
    else:
        print(f"     429 相对裸成本的额外等待 ≈ {extra:.0f}ms"
              + ("　→ fail-fast 生效" if extra < 50
                 else "　→ 还在重试（retry>0）或跑的是旧代码"))

    # ② 主场景
    raw = await asyncio.gather(
        *[timed_add(client, base, token, f"{title_prefix}_{i}") for i in range(n)],
    )
    dist: dict[int, int] = {}
    for s, _, _ in raw:
        dist[s] = dist.get(s, 0) + 1
    dist = dict(sorted(dist.items()))
    ok_main = [b["data"]["id"] for s, b, _ in raw if s == 200 and isinstance(b, dict)
               and b.get("data") and b["data"].get("id")]
    ok_ids.extend(ok_main)
    k, k_fp = len(ok_main), len(ok_ids) - len(ok_main)
    lat_ok = [lat for s, _, lat in raw if s == 200]
    lat_429 = [lat for s, _, lat in raw if s == 429]
    others = {c: v for c, v in dist.items() if c not in (200, 429)}

    print(f"  ③ 主场景 状态码分布：{dist}")
    print(f"     成功 {k}（指纹轮另计 {k_fp}）/ 429 拒绝 {len(lat_429)}"
          + (f" / 其他异常 {others}" if others else ""))
    print("     逐条：" + "　".join(f"{s}/{lat:.0f}ms" for s, _, lat in raw))
    print(f"     耗时：200 p50={pct(lat_ok, 0.5):.0f}ms　"
          f"429 p50={pct(lat_429, 0.5):.0f}ms min={min(lat_429) if lat_429 else 0:.0f}ms")

    # 数据面核对：库里实际落了几篇（指纹轮的成功也要算进总数）
    total_ok = len(ok_ids)
    await asyncio.sleep(0.5)  # 等 background RAG 提交完、列表缓存失效生效
    in_db = await count_by_keyword(client, base, title_prefix)
    print(f"     数据核对：keyword 搜索到 {in_db} 篇（应等于成功数 {total_ok}）"
          + ("✅" if in_db == total_ok else "❌ 不一致！"))

    # 判据优先级：独占探针（无并发污染）> 3 并发指纹 > 主场景中位数
    if probe_lat is not None and probe_status == 429:
        reject_wait, src = probe_lat - base_cost, "独占探针"
    elif extra is not None:
        reject_wait, src = extra, "3 并发指纹"
    else:
        reject_wait, src = None, "无"
    fail_fast = reject_wait is not None and reject_wait < 50
    clean = in_db == total_ok

    if others:
        print("  ❌ FAIL：出现非 200/429 的状态码，先看服务端日志")
    elif not clean:
        print(f"  ❌ FAIL：状态码与数据面不一致（库里 {in_db} ≠ 成功 {total_ok}），先查并发写库")
    elif fail_fast and k <= 5:
        print(f"  ✅ PASS：互斥成立（{src}测得额外等待≈0 → fail-fast 生效）；主场景 {k}/{n} 成功"
              f"是请求到达 stagger 落在锁空闲窗口所致，数据面一致")
    elif fail_fast:
        print(f"  ⚠️ WARN：fail-fast 已生效，但主场景 {k}/{n} 成功偏多 → 到达间隔 ≥ 临界区时长，"
              f"锁挡不住「先后到达」的请求；真正防重仍需幂等键 / UniqueConstraint 兜底")
    else:
        wait_txt = f"{reject_wait:.0f}ms（来源：{src}）" if reject_wait is not None else "未知"
        print(f"  ⚠️ 被拒请求额外等待 ≈{wait_txt}。这不是「锁没生效」，而是拒绝**延迟返回**了，"
              f"两种常见原因：\n"
              f"      a) acquire() 的 sleep 写在循环末尾 → 最后一次失败后仍空等一个 retry_delay\n"
              f"         （实现在 services/redis_lock.py:25-31，改成 if i < retry - 1 才 sleep）\n"
              f"      b) 运行环境不是最新代码（容器忘了 --build / 改的是宿主机文件）\n"
              f"      → 若 b) 已排除（镜像构建时间 = 今晚），那就是 a)，属延迟 bug 而非正确性 bug")

    s1_ids.extend(ok_ids)  # 复用清理列表
    return k


async def s3_two_users(client, base, token_a, user2, pwd2, n_each=5):
    """S3 双用户并发：验证锁粒度是按 user_id 隔离的。"""
    print(f"\n[S3] 双用户并发 各x{n_each}（锁粒度：不同用户互不干扰）")
    token_b = await login(client, base, user2, pwd2)
    title_a, title_b = make_title(), make_title()
    (ra, rb) = await asyncio.gather(
        asyncio.gather(*[add_blog(client, base, token_a, f"{title_a}_{i}")
                         for i in range(n_each)]),
        asyncio.gather(*[add_blog(client, base, token_b, f"{title_b}_{i}")
                         for i in range(n_each)]),
    )
    ok_a = sum(1 for s, _ in ra if s == 200)
    ok_b = sum(1 for s, _ in rb if s == 200)
    print(f"  用户A：{fmt_results(ra)}　用户B：{fmt_results(rb)}")
    if ok_a == n_each and ok_b == n_each:
        print("  ✅ PASS：不同用户互不挡，锁粒度（按 user_id）正确")
    else:
        print("  ❌ FAIL：不同用户被互相挡了，检查锁 key 是否漏了 user_id")
    for s, b in list(ra) + list(rb):
        if s == 200 and b.get("data"):
            s1_ids.append(b["data"]["id"])


async def s4_list_qps(client, base, total=60, conc=10):
    """S4 列表接口 QPS：顺带看缓存层的吞吐。响应 message 带“(缓存)”可区分命中。"""
    print(f"\n[S4] list_blogs 压测 {total} 次 / 并发 {conc}")
    sem = asyncio.Semaphore(conc)
    latencies, cache_hits = [], 0

    async def one():
        nonlocal cache_hits
        async with sem:
            t0 = time.perf_counter()
            r = await client.get(f"{base}/api/blogs/list_blogs",
                                 params={"page": 1, "pageSize": 10})
            latencies.append((time.perf_counter() - t0) * 1000)
            if "(缓存)" in r.json().get("message", ""):
                cache_hits += 1

    t0 = time.perf_counter()
    await asyncio.gather(*[one() for _ in range(total)])
    wall = time.perf_counter() - t0
    lat = sorted(latencies)
    p50, p95 = lat[len(lat) // 2], lat[int(len(lat) * 0.95)]
    print(f"  QPS ≈ {total / wall:.0f}　p50={p50:.0f}ms　p95={p95:.0f}ms"
          f"　缓存命中 {cache_hits}/{total}")
    if cache_hits == 0:
        print("  ⚠️ 0 命中：缓存层可能没生效（或首次请求把缓存击穿了？值得想）")


async def cleanup(client, base, token):
    if not s1_ids:
        return
    print(f"\n[清理] 软删压测文章 x{len(s1_ids)}")
    for bid in s1_ids:
        status = await delete_blog(client, base, token, bid)
        if status != 200:
            print(f"  ⚠️ 删除 id={bid} 返回 {status}（手动去后台清）")
    print("  完成")


# ---------------------------------------------------------------- main


async def main():
    args = parse_args()
    base = args.base_url.rstrip("/")
    async with httpx.AsyncClient(timeout=httpx.Timeout(15)) as client:
        # 健康检查
        try:
            r = await client.get(f"{base}/health")
            print(f"[预热] /health → {r.status_code}")
        except Exception as e:
            sys.exit(f"❌ 后端不可达：{base}（{e}）\n先起 docker compose 的 mysql/redis，再起 uvicorn")

        token = await login(client, base, args.user, args.password)
        print(f"[登录] {args.user} ✅")

        uid = await get_my_id(client, base, token)
        print(f"[用户] id={uid}（独占探针的锁 key = lock:add_blog:{uid}）")

        await s1_serial(client, base, token)
        await s2_same_user(client, base, token, args.concurrency, uid=uid,
                           redis_url=args.redis_url, no_probe=args.no_probe)
        if args.user2:
            await s3_two_users(client, base, token, args.user2, args.password2)
        else:
            print("\n[S3] 跳过（未提供 --user2）")
        await s4_list_qps(client, base, total=args.qps_n)
        await cleanup(client, base, token)

    print("\n压测结束。把输出整段发回去，重点看 S2 的判定行。")


if __name__ == "__main__":
    asyncio.run(main())
