# ====== 第一阶段：编译 Vue ======
FROM node:22-alpine AS builder
WORKDIR /app
# 先复制 package.json，利用层缓存
COPY package.json ./
# 安装依赖
RUN npm install
# 复制源代码
COPY . .
# 构建生产版本，输出到 dist/
RUN npm run build
# ====== 第二阶段：nginx 提供静态文件 ======
FROM nginx:alpine
# 设置时区
ENV TZ=Asia/Shanghai
# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf
# 从第一阶段复制编译产物到 nginx 静态目录
COPY --from=builder /app/dist /usr/share/nginx/html
# 暴露 80 端口
EXPOSE 80
# nginx 默认前台启动，无需额外配置
CMD ["nginx", "-g", "daemon off;"]
