from fastapi import FastAPI, Depends, HTTPException, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
import models, schemas, auth
from models import Product, CartItem, User

# создаём таблицы в БД при старте приложения
Base.metadata.create_all(bind=engine)

app = FastAPI()

# подключаем статику (картинки, css и т.д.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# подключаем шаблоны Jinja2
templates = Jinja2Templates(directory="templates")


# получаем сессию базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# вытаскиваем пользователя по токену
def get_current_user(db: Session, access_token: str):
    username = auth.verify_token(access_token)
    if not username:
        return None
    return db.query(User).filter(User.username == username).first()


# считаем скидку в зависимости от общей суммы покупок
def get_discount(total_spent: float):
    if total_spent >= 1000:
        return 0.10
    elif total_spent >= 500:
        return 0.05
    elif total_spent >= 100:
        return 0.02
    return 0


# главная страница
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# регистрация
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = auth.get_user_by_username(db, user.username)

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = auth.create_user(db, user.username, user.password)

    # создаём токен и сразу логиним пользователя
    token = auth.create_access_token({"sub": new_user.username})

    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)

    return response


# логин
@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = auth.get_user_by_username(db, user.username)

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = auth.create_access_token({"sub": db_user.username})

    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)

    return response


# выход из аккаунта
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/?logout=1", status_code=302)
    response.delete_cookie("access_token")
    return response


# страница логина
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# страница регистрации
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# профиль пользователя
@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, access_token: str = Cookie(None)):
    if not access_token:
        return RedirectResponse(url="/login")

    username = auth.verify_token(access_token)

    if not username:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "username": username}
    )


# обновление профиля
@app.post("/profile/update")
def update_profile(
    full_name: str,
    birth_date: str,
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(db, access_token)

    user.full_name = full_name
    user.birth_date = birth_date

    db.commit()

    return {"message": "Updated"}


# список товаров
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


# магазин (страница)
@app.get("/shop", response_class=HTMLResponse)
def shop(request: Request, access_token: str = Cookie(None)):
    if not access_token:
        return RedirectResponse(url="/login")

    username = auth.verify_token(access_token)
    if not username:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("shop.html", {"request": request})


# добавляем товары в БД при первом запуске
def seed_products():
    db = SessionLocal()

    if db.query(Product).count() == 0:
        products = [
            Product(
                name="Газировка",
                price=999,
                image="static/pictures/Газировка.jpg",
                description="Apple smartphone"
            ),
            Product(
                name="Кофе",
                price=1500,
                image="static/pictures/Кофе.jpg",
                description="Powerful laptop"
            ),
            Product(
                name="Наполеон",
                price=199,
                image="static/pictures/Наполеон.jpg",
                description="Noise cancelling"
            ),
        ]
        db.add_all(products)
        db.commit()

    db.close()


seed_products()


# добавить товар в корзину
@app.post("/cart/add/{product_id}")
def add_to_cart(product_id: int, access_token: str = Cookie(None), db: Session = Depends(get_db)):
    user = get_current_user(db, access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    item = db.query(CartItem).filter_by(user_id=user.id, product_id=product_id).first()

    if item:
        item.quantity += 1
    else:
        item = CartItem(user_id=user.id, product_id=product_id, quantity=1)
        db.add(item)

    db.commit()
    return {"message": "Added"}


# уменьшить количество товара
@app.post("/cart/decrease/{product_id}")
def decrease(product_id: int, access_token: str = Cookie(None), db: Session = Depends(get_db)):
    user = get_current_user(db, access_token)

    item = db.query(CartItem).filter_by(user_id=user.id, product_id=product_id).first()

    if item:
        item.quantity -= 1
        if item.quantity <= 0:
            db.delete(item)

    db.commit()
    return {"message": "Updated"}


# получить корзину
@app.get("/cart")
def get_cart(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    user = get_current_user(db, access_token)

    items = db.query(CartItem).filter_by(user_id=user.id).all()

    result = []
    for i in items:
        result.append({
            "id": i.product.id,
            "name": i.product.name,
            "price": i.product.price,
            "quantity": i.quantity
        })

    return result


# баланс пользователя
@app.get("/balance")
def get_balance(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    user = get_current_user(db, access_token)
    return {"balance": user.balance}


# пополнить баланс
@app.post("/balance/add")
def add_balance(amount: float, access_token: str = Cookie(None), db: Session = Depends(get_db)):
    user = get_current_user(db, access_token)

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    user.balance += amount
    db.commit()

    return {"balance": user.balance}


# оформление покупки
@app.post("/cart/checkout")
def checkout(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    user = get_current_user(db, access_token)

    items = db.query(CartItem).filter_by(user_id=user.id).all()

    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0

    for item in items:
        total += item.product.price * item.quantity

    # считаем скидку
    discount = get_discount(user.total_spent)
    final_price = total * (1 - discount)

    if user.balance < final_price:
        raise HTTPException(status_code=400, detail="Not enough money")

    # списываем деньги
    user.balance -= final_price

    # обновляем статистику трат
    user.total_spent += final_price

    # очищаем корзину
    for item in items:
        db.delete(item)

    db.commit()

    return {
        "message": "Purchase successful",
        "balance": user.balance,
        "discount": discount,
        "total_spent": user.total_spent
    }


# данные профиля (для фронта)
@app.get("/profile/data")
def get_profile_data(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    user = get_current_user(db, access_token)

    return {
        "username": user.username,
        "full_name": user.full_name,
        "birth_date": user.birth_date,
        "balance": user.balance,
        "total_spent": user.total_spent,
        "discount": get_discount(user.total_spent)
    }