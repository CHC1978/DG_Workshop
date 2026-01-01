# ============================================
# 後端 Dockerfile - 多階段構建，ARM64 相容
# Marine Equipment QR Management System
# ============================================

# Stage 1: Builder - 安裝 Python 依賴
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

# 安裝編譯依賴（bcrypt、Pillow 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - 最終映像
FROM python:3.12-slim-bookworm AS runtime

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Taipei

# 安裝運行時依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    libpng16-16 \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime

# 建立非 root 用戶（安全性）
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

WORKDIR /app

# 從 builder 階段複製 Python 套件
COPY --from=builder /root/.local /home/appuser/.local

# 複製應用程式碼
COPY --chown=appuser:appuser . .

# 建立必要目錄並設定權限
RUN mkdir -p /app/data /app/uploads \
    && chown -R appuser:appuser /app/data /app/uploads

# 切換到非 root 用戶
USER appuser

# 設定 PATH 以包含用戶安裝的套件
ENV PATH="/home/appuser/.local/bin:$PATH"

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 啟動命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
