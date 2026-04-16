from pydantic import BaseModel

# модель для создания пользователя
class UserCreate(BaseModel):
    username: str
    password: str


# модель для логина пользователя
class UserLogin(BaseModel):
    username: str
    password: str


# модель товара, который отдаём/храним в API
class Product(BaseModel):
    id: int
    name: str
    price: float
    image: str
    description: str

    class Config:
        # нужно, чтобы Pydantic нормально работал с ORM
        from_attributes = True