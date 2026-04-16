from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# таблица пользователей
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # логин и пароль пользователя
    username = Column(String, unique=True, index=True)
    password = Column(String)

    # баланс пользователя (деньги на счету)
    balance = Column(Float, default=0)

    # дополнительные данные профиля
    full_name = Column(String, default="Иван Иванов")
    birth_date = Column(String, default="2000-01-01")

    # сколько всего пользователь потратил
    total_spent = Column(Float, default=0)


# таблица товаров
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    image = Column(String)
    description = Column(String)


# элементы корзины пользователя
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)

    # связи с пользователем и товаром
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    # сколько штук товара в корзине
    quantity = Column(Integer, default=1)

    # связь с товаром (чтобы удобно доставать product из cart item)
    product = relationship("Product")