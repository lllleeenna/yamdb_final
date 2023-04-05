# CI и CD проекта api_yamdb
[![Github CI/CD](https://github.com/lllleeenna/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/lllleeenna/yamdb_final/actions/)

Настройка для приложения Continuous Integration и Continuous Deployment:
### Workflow
- tests - проверка кода на соответствие pep8, автоматический запуск тестов
- build_and_push_to_docker_hub - обновление образов на Docker Hub,
- deploy - автоматический деплой на боевой сервер при пуше в главную ветку main.
- send_message - отправка сообщения об успешном деплое в Telegram

### Запуск
Отредактируйте файл nginx/default.conf и в строке server_name впишите 
IP сервера.
Скопируйте файлы docker-compose.yaml и nginx/default.conf из вашего проекта 
на сервер в home/<ваш_username>/docker-compose.yaml и 
home/<ваш_username>/nginx/default.conf соответственно.
```
scp docker-compose.yaml <username>@<host>/home/<username>/docker-compose.yaml
sudo mkdir nginx
scp default.conf <username>@<host>/home/<username>/nginx/default.conf
```
В репозитории на Github добавьте данные в Settings - Secrets - Actions secrets:
```
DOCKER_USERNAME - имя пользователя DockerHub
DOCKER_PASSWORD - пароль пользователя DockerHub
HOST - ip-адрес сервера
USER - пользователь
SSH_KEY - приватный ssh-ключ (публичный должен быть на сервере)
PASSPHRASE - кодовая фраза для ssh-ключа
DB_ENGINE - django.db.backends.postgresql
DB_HOST - db
DB_PORT - 5432
TELEGRAM_TO - id своего телеграм-аккаунта (можно узнать у @userinfobot)
TELEGRAM_TOKEN - токен Telegram бота
DB_NAME - имя БД
POSTGRES_USER - пользователь БД
POSTGRES_PASSWORD - пароль для БД
```
После деплоя на сервере

Выполнить миграции:

```
sudo docker-compose exec web python manage.py migrate
```

Создайте суперпользователя:

```
sudo docker-compose exec web python manage.py createsuperuser
```

Соберите статику:

```
sudo docker-compose exec web python manage.py collectstatic --no-input
```
http://158.160.59.102/api/v1/

http://158.160.59.102/admin/
 