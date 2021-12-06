# yamdb_final
### Описание проекта:
Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Книги», «Фильмы», «Музыка».
### Технологии
Python 3.7-slim
Django 2.2.16
Docker 20.10.10
### Шаблон наполнения env-файла:
```DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
```
```
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
```
```
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
```
```
DB_HOST=db # название сервиса (контейнера)
```
```
DB_PORT=5432 # порт для подключения к БД
```
### Адрес сервера, с развернутым приложением
51.250.9.140

# yamdb_final
yamdb_final
![example workflow](https://github.com/RuslanRD/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
