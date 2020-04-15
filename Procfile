release: python app/manage.py migrate
web: cd app; daphne app.asgi:application -p $PORT -b 0.0.0.0