"""FastAPI 應用程式入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.csrf import CSRFMiddleware

# 初始化 rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("Starting application...")
    await init_db()
    print("Database initialized successfully")

    yield

    # Shutdown
    print("Shutting down application...")
    await close_db()
    print("Database connection closed")


# 建立 FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Marine Equipment QR Management System API",
    lifespan=lifespan,
)

# 設定 rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 設定 CORS (限制方法和標頭以提高安全性)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 明確列出允許的方法
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "X-CSRF-Token",
        "Accept",
        "Accept-Language",
        "Content-Language",
    ],  # 明確列出允許的標頭
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=600,  # CORS 預檢快取 10 分鐘
)

# 添加 CSRF 保護 Middleware (Double Submit Cookie 模式)
app.add_middleware(CSRFMiddleware)


# 添加安全標頭中介軟體
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """添加安全相關的 HTTP 標頭"""
    response = await call_next(request)

    # 防止 MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # 防止點擊劫持 (Clickjacking)
    response.headers["X-Frame-Options"] = "DENY"

    # XSS 保護 (舊版瀏覽器)
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # HSTS (HTTP Strict Transport Security) - 僅在 HTTPS 時啟用
    if settings.DEBUG:
        # 開發環境使用較短的時間
        response.headers["Strict-Transport-Security"] = "max-age=0"
    else:
        # 生產環境強制 HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Content Security Policy
    # 生產環境使用更嚴格的 CSP，開發環境允許必要的例外
    if settings.DEBUG:
        # 開發模式: Vue 需要 unsafe-eval 和 unsafe-inline
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' ws: wss:",  # 允許 WebSocket (Vite HMR)
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
    else:
        # 生產模式: 更嚴格的 CSP
        csp_directives = [
            "default-src 'self'",
            "script-src 'self'",  # 移除 unsafe-inline 和 unsafe-eval
            "style-src 'self' 'unsafe-inline'",  # Tailwind 仍需要 unsafe-inline
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "upgrade-insecure-requests",  # 強制 HTTPS
        ]
    response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

    # 額外安全標頭
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    # 移除可能洩露信息的標頭 (MutableHeaders 沒有 pop 方法，使用 del)
    if "Server" in response.headers:
        del response.headers["Server"]
    if "X-Powered-By" in response.headers:
        del response.headers["X-Powered-By"]

    return response


@app.get("/")
async def root():
    """根路徑"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}


# Register API routers
from app.api import api_router
app.include_router(api_router, prefix="/api")

# Mount static files for uploads
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
