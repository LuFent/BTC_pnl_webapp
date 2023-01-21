# Калькулятор прибыли на бирже Derbit
Веб-приложение которое получает по API информацию с биржи Derbit и выводит информацию о прибыли за определенный период. Фронтенд делает запросы AJAX-ом на вьюху get_currencies_data_by_period. Данные с биржи приложение получает managment командой.

## Запуск локально

1) Скачайте репозиторий и перейдите в него
```
git clone git@github.com:LuFent/stripe_shop_webapp.git
cd stripe_shop_webapp
```

 2) *(Опционально)* создайте виртуальное окружение
```
virtualenv venv
source ./venv/bin/activate
```

3) Скачайте зависимости
```
pip3 install -r requirements.txt
```

4) [Получите ID Секрет клиента Derbit](https://test.deribit.com/account/BTC/api)



5) Создайте .env файл с таким содержанием:
```
DERBIT_CLIENT_ID="<ID Клиента>"
DERBIT_CLIENT_SECRET="<Секрет Клиента>"
REDIS_HOST="<HOST Редиса>"
REDIS_PORT ="<PORT Редиса>"
REDIS_DB_NUM="<Номер БД Редиса>"
```

6) Выполните миграции командой
```
python3 manage.py migrate
```

7) Создайте админа командой
```
python3 manage.py createsuperuser
<Введите имя и пароль, поле email можно оставить пустым>
```

8) Запустите сайт на локалхосте командой
```
python3 manage.py runserver
```

9) Поставьте команду  **pull_derbit_data** на таймер, чтобы она выполнялась каждые 10 секунд или выберете другой период. Это можно сделать например командой
```
watch -n 10 python3 manage.py pull_derbit_data
```
 во втором терминале(не забудьте активировать окружение если создавали его)

10) Главная страница сайта будет доступна по адресу http://127.0.0.1:8000/


 ## Цели проекта

 Проект выполнен в качестве тестового задания на вакаснию.
