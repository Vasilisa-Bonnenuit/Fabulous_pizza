import re
import hashlib

# Хранилище пользователей (в реальном приложении — база данных)

users = {}

def is_valid_email(email):
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def hash_password(password):

    #Хэширует пароль с помощью SHA-256

    return hashlib.sha256(password.encode()).hexdigest()

def register_user():
   
    print("=== Регистрация нового пользователя ===")
    
    # Ввод имени
    while True:
        username = input("Введите имя пользователя: ").strip()
        if username:
            break
        print("Имя пользователя не может быть пустым!")
    
    # Ввод email
    while True:
        email = input("Введите email: ").strip().lower()
        if is_valid_email(email):
            if email in users:
                print("Этот email уже зарегистрирован!")
                continue
            break
        else:
            print("Некорректный email! Попробуйте снова.")
    
    # Ввод пароля
    while True:
        password = input("Введите пароль (не менее 8 символов, должны быть буквы и цифры): ").strip()
        if is_valid_password(password):
            break
        else:
            print("Пароль не соответствует требованиям! Попробуйте снова.")
    
    # Подтверждение пароля
    while True:
        confirm_password = input("Повторите пароль: ").strip()
        if password == confirm_password:
            break
        print("Пароли не совпадают! Попробуйте снова.")
    
    # Сохраняем пользователя (пароль — в хэшированном виде)
    users[email] = {
        'username': username,
        'password_hash': hash_password(password)
    }
    
    print(f"\nРегистрация успешна! Пользователь {username} добавлен.")

def main():
    
    while True:
        print("\n=== Меню ===")
        print("1. Зарегистрироваться")
        print("2. Выйти")
        choice = input("Выберите действие (1-2): ").strip()
        
        if choice == '1':
            register_user()
        elif choice == '2':
            print("До свидания!")
            break
        else:
            print("Неверный выбор! Попробуйте снова.")

# Запуск приложения
if __name__ == "__main__":

    main()