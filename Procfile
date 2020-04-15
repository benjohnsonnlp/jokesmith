release: python app/manage.py migrate
web: cd app; daphne app.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2