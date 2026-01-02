"""CSRF 保護機制 - Double Submit Cookie 模式"""
import secrets
from typing import Callable, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


# CSRF Token 長度 (32 bytes = 43 字元 base64url)
CSRF_TOKEN_BYTES = 32

# Cookie 名稱
CSRF_COOKIE_NAME = "csrf_token"

# Header 名稱
CSRF_HEADER_NAME = "X-CSRF-Token"

# 安全方法 (不需要 CSRF 保護)
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

# 排除路徑 (登入前無 CSRF token 或低風險操作)
CSRF_EXEMPT_PATHS = {
    "/api/auth/login/step1",
    "/api/auth/login/step2",
    "/api/auth/login/backup-code",
    "/api/auth/refresh",
    "/api/auth/logout",  # Logout 有 token 驗證，且 CSRF 風險低
    "/docs",
    "/redoc",
    "/openapi.json",
}


def generate_csrf_token() -> str:
    """
    產生隨機 CSRF token

    Returns:
        43 字元的 URL 安全 base64 字串
    """
    return secrets.token_urlsafe(CSRF_TOKEN_BYTES)


def set_csrf_cookie(response: Response, token: Optional[str] = None) -> str:
    """
    設定 CSRF cookie

    Args:
        response: FastAPI Response 物件
        token: 可選的 CSRF token，若未提供則自動產生

    Returns:
        設定的 CSRF token
    """
    if token is None:
        token = generate_csrf_token()

    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,  # 前端需要讀取
        secure=settings.SECURE_COOKIE,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 與 refresh token 同步
        path="/",
    )

    return token


def clear_csrf_cookie(response: Response) -> None:
    """
    清除 CSRF cookie

    Args:
        response: FastAPI Response 物件
    """
    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        secure=settings.SECURE_COOKIE,
        samesite="lax",
    )


def verify_csrf_token(request: Request) -> bool:
    """
    驗證 CSRF token (cookie vs header)

    Args:
        request: FastAPI Request 物件

    Returns:
        True 如果驗證通過，否則 False
    """
    # 從 cookie 取得 token
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    if not cookie_token:
        return False

    # 從 header 取得 token
    header_token = request.headers.get(CSRF_HEADER_NAME)
    if not header_token:
        return False

    # 使用 secrets.compare_digest 防止時序攻擊
    return secrets.compare_digest(cookie_token, header_token)


def is_csrf_exempt(request: Request) -> bool:
    """
    檢查請求是否豁免 CSRF 驗證

    Args:
        request: FastAPI Request 物件

    Returns:
        True 如果豁免，否則 False
    """
    # 安全方法不需要 CSRF 保護
    if request.method in SAFE_METHODS:
        return True

    # 排除特定路徑
    path = request.url.path
    if path in CSRF_EXEMPT_PATHS:
        return True

    # 以排除路徑開頭的也豁免
    for exempt_path in CSRF_EXEMPT_PATHS:
        if path.startswith(exempt_path):
            return True

    return False


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF 保護 Middleware

    實作 Double Submit Cookie 模式:
    1. 登入時設定 CSRF cookie (非 httpOnly)
    2. 前端讀取 cookie，附加到 X-CSRF-Token header
    3. Middleware 驗證 header 值 = cookie 值
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        處理 CSRF 驗證

        Args:
            request: 進入的請求
            call_next: 下一個處理函式

        Returns:
            Response 物件

        Raises:
            HTTPException: 403 如果 CSRF 驗證失敗
        """
        # 檢查是否豁免
        if is_csrf_exempt(request):
            return await call_next(request)

        # 驗證 CSRF token
        if not verify_csrf_token(request):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token verification failed"},
            )

        return await call_next(request)
