# jokesmith

A dumb web app for joking.

![Django CI](https://github.com/benjohnsonnlp/jokesmith/workflows/Django%20CI/badge.svg)

## Heroku Deploy
1. `heroku addons:create heroku-redis:hobby-dev`

## Local startup with Docker
1. `docker run -d --name my_postgres -v my_dbdata:/var/lib/postgresql/data -p 54320:5432 -e POSTGRES_PASSWORD=postgres postgres`
2. `docker run --name my_redis -p 6379:6379 -d redis:5`
3. `export REDIS_URL=redis://localhost:6379`
4. `export DJANGO_DB=postgres`