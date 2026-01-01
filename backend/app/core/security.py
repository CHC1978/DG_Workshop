"""安全性相關功能: JWT, TOTP, 密碼雜湊"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import pyotp
from jose import JWTError, jwt
import bcrypt
import qrcode
import io
import base64

from app.core.config import settings

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    # Bcrypt has a 72 byte limit, encode to bytes
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    建立 JWT access token

    Args:
        data: 要編碼的資料 (通常包含 sub: user_id)
        expires_delta: 過期時間，預設使用設定檔的值

    Returns:
        JWT token 字串
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_temp_token(data: Dict[str, Any]) -> str:
    """
    建立臨時 token (用於兩階段認證)

    Args:
        data: 要編碼的資料

    Returns:
        臨時 token 字串
    """
    expires_delta = timedelta(minutes=settings.TEMP_TOKEN_EXPIRE_MINUTES)
    return create_access_token(data, expires_delta)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解碼 JWT token

    Args:
        token: JWT token 字串

    Returns:
        解碼後的 payload，若失敗則返回 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        # 不記錄敏感資訊 (token, secret_key)
        logger.warning(f"JWT decode failed: {type(e).__name__}")
        return None


# ==================== TOTP 2FA ====================

def generate_totp_secret() -> str:
    """產生 TOTP secret"""
    return pyotp.random_base32()


def get_totp_uri(secret: str, username: str, issuer: str = None) -> str:
    """
    取得 TOTP URI (用於產生 QR Code)

    Args:
        secret: TOTP secret
        username: 使用者名稱
        issuer: 發行者名稱 (預設使用 APP_NAME)

    Returns:
        otpauth:// URI
    """
    if issuer is None:
        issuer = settings.APP_NAME

    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=issuer)


def generate_qrcode_base64(data: str) -> str:
    """
    產生 QR Code 並轉為 base64 字串

    Args:
        data: 要編碼的資料 (通常是 TOTP URI)

    Returns:
        base64 編碼的 QR Code 圖片
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # 轉為 base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def verify_totp(secret: str, code: str) -> bool:
    """
    驗證 TOTP 碼

    Args:
        secret: TOTP secret
        code: 使用者輸入的 6 位數碼

    Returns:
        驗證是否成功
    """
    # 檢查 secret 是否有效
    if not secret or secret == "RESET":
        logger.warning("TOTP verification failed: invalid secret state")
        return False

    try:
        totp = pyotp.TOTP(secret)
        # valid_window=0: 嚴格驗證，只接受當前 30 秒窗口
        # 如果使用者時鐘有輕微偏差，可考慮設為 1
        return totp.verify(code, valid_window=0)
    except Exception as e:
        logger.warning(f"TOTP verification error: {type(e).__name__}")
        return False


def generate_backup_codes(count: int = 8) -> list[str]:
    """
    產生備用碼

    Args:
        count: 備用碼數量

    Returns:
        備用碼列表
    """
    import secrets
    return [secrets.token_hex(4).upper() for _ in range(count)]
