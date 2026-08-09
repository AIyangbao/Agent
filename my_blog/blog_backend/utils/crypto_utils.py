from cryptography.fernet import Fernet
import hmac
import hashlib
from config.settings import settings

_fernet = Fernet(settings.PHONE_ENCRYPTION_KEY.encode())

def encrypt_phone(plain: str) -> str:
    """AES 加密手机号，返回可存库的密文 token。"""
    return _fernet.encrypt(plain.encode()).decode()

def decrypt_phone(token: str)-> str | None:
    """解密手机号:token 损坏/密钥不符时返回 None,不抛异常。"""
    try:
        return _fernet.decrypt(token.encode()).decode()
    except Exception:
        return None

def hash_phone(plain: str) -> str:
        """确定性 HMAC 哈希，用于按手机号查重/查询，不可逆、防彩虹表。"""
        return hmac.new(
             settings.PHONE_ENCRYPTION_KEY.encode(),
             plain.encode(),
             hashlib.sha256,
        ).hexdigest()