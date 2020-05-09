FROM python:3.7-slim
ENV PYTHONUNBUFFERED=1 DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 PYTHONPATH=$PYTHONPATH:/jokesmith/
RUN mkdir /jokesmith
WORKDIR /jokesmith
COPY requirements.txt /jokesmith/
RUN apt-get -qq update \
    && mkdir -p /usr/share/man/man1/ && mkdir -p /usr/share/man/man3/ && mkdir -p /usr/share/man/man7/ \
    && apt-get -qq install -yq --no-install-recommends postgresql postgresql-client libpq-dev locales build-essential libssl-dev libffi-dev netbase \
    python-dev \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen \
    && pip install pip --upgrade


# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt \
    && apt-get remove --purge -yqq build-essential python-dev \
    && apt-get clean \
    && rm -rf \
        ~/.cache/pip/* \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base
COPY . /jokesmith/