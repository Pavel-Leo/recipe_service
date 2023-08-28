# **Foodgram project react**

## **Техническое описание проекта foodgram доступно из контейнера docker:**
http://localhost:9090/api/docs/

## **Стэк технологий**

Django==3.2

djangorestframework==3.12.4

djoser==2.2.0

psycopg2-binary==2.9.3

Pillow==8.1.0

nginx

React

PostgreSQL




## Описание

Проект foodgram позволяет размещать рецепты пользователей.
- Незарегистрированные пользователи могут просматривать рецепты на главной странице и сортировать их по тегам, просматривать отдельные страницы рецептов или пользователейь а также создать аккаунт.

- Зарегистрированные пользователи могут то же что не зарегистрированные, а так же входить в систему под своим логином и паролем и выходить из него, менять свой пароль, создавать, редактировать и удалять собственные рецепты, работать с персональным списком покупок: добавление и удаление любых рецептов, выгрузка файла с количеством необходимых ингредиентов для рецептов из списка покупок.
    Работать с персональным списком избранного: добавление в него рецептов или удаление их, просмотр своей страницы избранных рецептов.
    Подписываться на публикации авторов рецептов и отменять подписки, просматривать свою страницу подписок.

Регистрация:
- Пользователь отправляет POST-запрос с параметрами email, username, first_name, last_name, password на эндпоинт /api/users/ с параметрами:
```
{
"email": "vpupkin@yandex.ru",
"username": "vasya.pupkin",
"first_name": "Вася",
"last_name": "Пупкин",
"password": "Qwerty123"
}
```
Доступ предоставляется по токену
- Пользователь отправляет POST-запрос с параметрами username и email на эндпоинт /api/auth/token/login/
```
{
"password": "string",
"email": "string"
}
```

## Примеры запросов к API

### Регистрация пользователя

```http
  POST /api/users/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `email` | `string` | **Required**. Your email|
| `username` | `string` | **Required**|
| `first_name` | `string` | **Required**|
| `last_name` | `string` | **Required**|
| `password` | `string` | **Required**|

### Получение токена для аутентификации

```http
  POST /api/auth/token/login/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `password` | `string` | **Required**.|
| `email` | `string` | **Required**.|



## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:Pavel-Leo/foodgram-project-react.git
```

```
cd foodgram-project-react
```

:exclamation: Идеально было бы в корневой папке там же где располагаются репозитории backend, frontend и тд создать файл .env. Заполнение файла можно взять из .env.example или из кода ниже:

```
SECRET_KEY='kb23&&e3h52665ng&9af=y_-h_-2j5t97wlqxja6gg$$_0jpu'
DEBUG=False
ALLOWED_HOSTS='localhost,127.0.0.1,ваш IP адрес,ваш домен'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
DB_NAME=postgres
DB_HOST=db
DB_PORT=5432
```

Из корневой папки где находится файл docker-compose.yml выполнить команды по очереди:

```
docker compose -f docker-compose.yml exec backend python manage.py makemigrations
docker compose -f docker-compose.yml exec backend python manage.py migrate
docker compose -f docker-compose.yml exec backend python manage.py collectstatic

если вы работате на windows в git bash то следующую команду следует выполнить из Windows PoweShell из того же репозитория где находится файл docker-compose.yml чтобы пути построились верно:
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/

Заполните базу данными командной
docker compose -f docker-compose.yml exec backend python manage.py import_csv

Создайте суперпользователя:
docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```

:exclamation: Чтобы позже можно было создавать рецепты необходимо создать тэги через админ зону
http://localhost:9090/admin/recipes/tag/

указать цвет нужно в формате hex, например, #D2691E
Цвета вы можете найти по адресу:
https://colorscheme.ru/html-colors.html


Теперь вы можете перейти по адресу http://localhost:9090/recipes
cоздать пользователя и пользоваться приложением.



## Автор
- Леонтьев Павел https://github.com/Pavel-Leo