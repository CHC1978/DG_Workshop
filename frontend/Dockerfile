# ============================================
# 前端 Dockerfile - 構建靜態文件 + Nginx 服務
# Marine Equipment QR Management System
# ============================================

# Stage 1: Build - 使用 Bun 構建 Vue 應用
FROM oven/bun:1.1-alpine AS builder

WORKDIR /app

# 複製 package.json 和 lockfile
COPY package.json bun.lockb* ./

# 安裝依賴
RUN bun install --frozen-lockfile

# 複製原始碼
COPY . .

# 構建生產版本
RUN bun run build

# Stage 2: Runtime - Nginx 服務靜態文件
FROM nginx:1.25-alpine AS runtime

# 設定時區
ENV TZ=Asia/Taipei

RUN apk add --no-cache tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime

# 移除預設配置
RUN rm /etc/nginx/conf.d/default.conf

# 複製自訂 Nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 從 builder 階段複製構建產物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# 啟動 Nginx
CMD ["nginx", "-g", "daemon off;"]
