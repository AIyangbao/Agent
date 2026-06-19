from passlib.context import CryptContext
# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

# 密码加密
def get_hash_password(password: str):
    # bcrypt 现在密码不超过72子节
    password_bytes = password.encode('utf-8')
    if len(password.encode('utf-8')) > 72:
        password = password_bytes[:72].decode('utf-8',errors='ignore')
    return pwd_context.hash(password)

# 密码验证: verify 返回值是布尔型
def verify_password(plain_password,hash_password):
    return pwd_context.verify(plain_password,hash_password)
