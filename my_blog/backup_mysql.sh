#!/usr/bin/env bash
# ============================================================
# 博客 MySQL 自动备份脚本（部署在阿里云 ECS 宿主机上运行）
# 用法：
#   1) chmod +x backup_mysql.sh
#   2) 手动试跑：./backup_mysql.sh
#   3) 加入 cron（每天 04:00）：
#      crontab -e  ->  0 4 * * * /path/to/backup_mysql.sh >> /var/log/blog_backup.log 2>&1
# 说明：
#   - 通过 docker exec 进 blog-mysql 容器执行 mysqldump（官方 mysql 镜像自带）
#   - 密码用 MYSQL_PWD 环境变量传入，避免出现在 ps 进程列表
#   - 备份文件含全量数据（含用户密码哈希），存于服务器本地，务必限制权限（见下方 chmod）
# ============================================================
set -euo pipefail

# ===== 配置 =====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
# 默认备份到仓库内的 backups/ 子目录（跨平台：Windows Git Bash / Linux 都明确）
# 生产服务器想换路径可覆盖：BACKUP_DIR=/var/backups/blog_mysql ./backup_mysql.sh
BACKUP_DIR="${BACKUP_DIR:-$SCRIPT_DIR/backups}"
RETENTION_DAYS=7
CONTAINER="blog-mysql"
DB_NAME="${DB_NAME:-blog_db}"
LOG_FILE="${BACKUP_DIR}/backup.log"

# 读取 .env（仅导出用到的变量）
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

MYSQL_PWD="${DB_PWD:?请在 .env 中设置 DB_PWD}"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"          # 备份含敏感数据，目录仅 owner 可读

TS="$(date +%Y%m%d_%H%M%S)"
OUT="$BACKUP_DIR/${DB_NAME}_${TS}.sql.gz"

echo "[$(date)] 开始备份 ${DB_NAME} -> $OUT" | tee -a "$LOG_FILE"

# --single-transaction：InnoDB 在线热备不锁表；--routines/--events：连带存储过程与事件
if docker exec -e MYSQL_PWD="$MYSQL_PWD" "$CONTAINER" \
    mysqldump -uroot --single-transaction --routines --events "$DB_NAME" \
    | gzip -9 > "$OUT"; then
  chmod 600 "$OUT"
  echo "[$(date)] 备份成功: $(du -h "$OUT" | cut -f1)" | tee -a "$LOG_FILE"
else
  echo "[$(date)] 备份失败!" | tee -a "$LOG_FILE"
  rm -f "$OUT"
  exit 1
fi

# 清理超过保留期的旧备份
DELETED=$(find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete -print | wc -l)
echo "[$(date)] 已清理 ${DELETED} 个超过 ${RETENTION_DAYS} 天的旧备份" | tee -a "$LOG_FILE"
