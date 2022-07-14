# Проект соцсети Yatube

## Описание проекта

Проект по созданию соцсети с возможностью регистрации, создания групп, постов с картинками, подписок на любимых авторов и комментирования. Большая часть проекта покрыта Unit-тестами

## Установка проекта локально

В папке склонированного репозитория выполните:

```bash
cd yatube
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser --email admin@admin.com --username admin -v 3
```
Задайте пароль для суперпользователя. Логин суперпользователя - admin. При заполнении БД тестовыми данными, суперпользователь уже создан. `Login: admin, pass: admin`
Затем
```Bash
python3 manage.py runserver
```
Для проверки работоспособности, перейдите на http://127.0.0.1:8000/


## Заполнение БД тестовыми данными

```bash
python3 manage.py loaddata ../fixtures/fixtures.json
```

## Стек

Django, Django ORM, Unittest, OOP, django-debug-toolbar

## Автор

Семён Егоров

[LinkedIn](https://www.linkedin.com/in/simonegorov/)  
[Email](rhinorofl@gmail.com)  
[Telegram](https://t.me/SamePersoon)