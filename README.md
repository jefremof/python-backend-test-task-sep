# Тестовое задание Python Backend Developer

## Запуск
Dev-контейнер:\
`docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml up --build`

Prod-контейнер:\
`docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up --build`

Для запуска требуется определить переменные среды `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`, `API_KEY` вручную или с помощью `.env` файла.

## Заполнение тестовыми данными
Производится с помощью скрипта:\
`python -m src.scripts.seed.py`\
(Автоматически происходит при запуске dev-контейнера)

## Документация
Доступна после запуска приложения:\
`http://127.0.0.1:8000/docs`\
`http://127.0.0.1:8000/redoc`
