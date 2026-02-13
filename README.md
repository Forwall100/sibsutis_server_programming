## Проект использует следующие технологии и библиотеки:
- **FastAPI** - основной веб-фреймворк для создания REST API. 
- **Pymongo** - драйвер для работы с MongoDB.
- **Argon2-cffi** - современный алгоритм для безопасного хэширования паролей.
- **Python-jose** - библиотека для работы с JWT-токенами.
- **Pydantic** - библиотека для валидации данных и управления настройками.

## Общая структура

```
app/
├── core/           # Базовые компоненты приложения
│   ├── config.py   # Конфигурация и настройки
│   └── database.py # Подключение к MongoDB
├── routers/        # API-эндпоинты (контроллеры)
│   ├── auth.py     # Аутентификация
│   ├── products.py # Товары
│   └── orders.py   # Заказы
├── schemas/        # Pydantic-модели (валидация)
├── utils/          # Утилиты
│   ├── auth.py     # Работа с JWT
│   └── password.py # Хэширование паролей
└── main.py         # Точка входа

```
## Аутентификация и авторизация

Аутентификация построена на стандарте JWT. При успешном входе пользователь получает токен доступа, который необходимо передавать в заголовке Authorization всех защищённых запросов.

При регистрации пароль хэшируется, при входе - верифицируется с помощью Argon2id.

Авторизация реализована на основе ролей. Простой пользователь имеет доступ к своему профилю и заказам. Администратор (is_admin=true) дополнительно может создавать товары.

Проверка прав реализована через зависимости FastAPI: get_current_user извлекает данные из токена, get_admin_user дополнительно проверяет флаг is_admin в базе данных.

## Структура данных в MongoDB

### Коллекция users
- `_id` - уникальный идентификатор ObjectId, генерируется монгой автоматически
- `email` - адрес электронной почты
- `username` - имя пользователя
- `password_hash` - хэш пароля
- `is_admin` - определяет права администратора

### Коллекция products
- `_id` - уникальный идентификатор
- `name` - название товара
- `description` - описание товара (опционально)
- `price` - цена товара
- `stock` - количество на складе

### Коллекция orders
- `_id` - уникальный идентификатор
- `user_id` - идентификатор пользователя (ссылка на users._id)
- `items` - массив товаров в заказе, каждый элемент содержит product_id, name, quantity и price
- `total` - общая сумма заказа
- `status` - статус заказа (по умолчанию «pending»)
- `created_at` - дата и время создания заказа

## Установка и запуск
```bash
uv sync
```

### Настройка переменных окружения

Создайте .env в корне проекта со следующим содержимым:

```env
MONGO_URL=mongodb://127.0.0.1:27017
DATABASE_NAME=shop
SECRET_KEY=your-secret-key-for-jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Запуск сервера

```bash
uv run python main.py
```

## Документация API

После запуска сервера документация Swagger UI доступна по адресу http://localhost:8000/docs, где можно и протестировать все эндпоинты.

### Публичные эндпоинты

#### POST /auth/register - Регистрация нового пользователя

Регистрирует нового пользователя в системе. Email должен быть уникальным. Возвращает данные созданного пользователя без пароля.

Тело запроса:

```json
{
  "email": "test@test.ru",
  "username": "test",
  "password": "krutoyparol"
}
```

Ответ:

```json
{
  "id": "698ef34b3061f18e8c7d7e25",
  "email": "test@test.ru",
  "username": "test",
  "is_admin": false
}
```

#### POST /auth/login - Вход в систему

Аутентифицирует пользователя и возвращает JWT-токен доступа. Принимает данные в формате application/x-www-form-urlencoded. Поле username должно содержать email пользователя.

Тело запроса:

```
username=test@test.ru&password=krutoyparol
```

Ответ:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Токен необходимо использовать в заголовке Authorization для защищённых запросов: `Authorization: Bearer {token}`.

#### GET /products - Получение списка товаров

Публичный эндпоинт, не требует аутентификации.

Ответ:

```json
[
  {
    "id": "678f1234567890abcdef0001",
    "name": "MacBook Pro",
    "description": "14-inch M3 Pro",
    "price": 1500.00,
    "stock": 10
  }
]
```

### Защищённые эндпоинты

#### GET /auth/me - Текущий пользователь

Возвращает информацию о пользователе, чей токен передан в заголовке Authorization. Требует валидный JWT-токен.

Заголовки:

```
Authorization: Bearer {token}
```

Ответ:

```json
{
  "id": "698ef34b3061f18e8c7d7e25",
  "email": "user@example.com",
  "username": "john_doe",
  "is_admin": false
}
```

#### POST /products  Создание товара

Создаёт новый товар. Требует is_admin=true для пользователя чей токен передан.

Заголовки:

```
Authorization: Bearer {token}
```

Тело запроса:

```json
{
  "name": "iPhone 15 Pro",
  "description": "256GB Space Black",
  "price": 999.00,
  "stock": 50
}
```

#### GET /orders
Возвращает все заказы текущего пользователя.

Заголовки:

```
Authorization: Bearer {token}
```

Ответ:

```json
[
  {
    "id": "678f1234567890abcdef0002",
    "user_id": "698ef34b3061f18e8c7d7e25",
    "items": [
      {
        "product_id": "678f1234567890abcdef0001",
        "name": "MacBook Pro",
        "quantity": 2,
        "price": 1500.00
      }
    ],
    "total": 3000.00,
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### POST /orders

Создаёт новый заказ для текущего пользователя. Автоматически вычисляет общую сумму на основе переданных товаров.

Заголовки:

```
Authorization: Bearer {token}
```

Тело запроса:

```json
{
  "items": [
    {
      "product_id": "678f1234567890abcdef0001",
      "name": "MacBook Pro",
      "quantity": 2,
      "price": 1500.00
    }
  ]
}
```

Ответ:

```json
{
  "id": "678f1234567890abcdef0004",
  "user_id": "698ef34b3061f18e8c7d7e25",
  "items": [
    {
      "product_id": "678f1234567890abcdef0001",
      "name": "MacBook Pro",
      "quantity": 2,
      "price": 1500.00
    }
  ],
  "total": 3000.00,
  "status": "pending",
  "created_at": "2024-01-15T12:00:00Z"
}
```

## Создание администратора

По умолчанию все зарегистрированные пользователи имеют статус обычного пользователя (is_admin=false). Для получения прав администратора необходимо вручную изменить значение в базе данных MongoDB.

```javascript
db.users.updateOne(
  { email: "test@test.ru" },
  { $set: { is_admin: true } }
)
```

