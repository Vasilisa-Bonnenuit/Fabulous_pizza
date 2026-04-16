from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from jose import JWTError, jwt
from datetime import datetime, timedelta

# ключ и настройки JWT (используется для токенов авторизации)
SECRET_KEY = "Dana123456Dana"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# хеширование паролей через argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# создаём JWT токен
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# проверяем токен и достаём username
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# хешируем пароль перед сохранением
def hash_password(password: str):
    return pwd_context.hash(password)


# проверяем пароль при логине
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# ищем пользователя в базе по username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# создаём нового пользователя
def create_user(db: Session, username: str, password: str):
    hashed = hash_password(password)
    db_user = User(username=username, password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user