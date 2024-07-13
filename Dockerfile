FROM python:3.12
LABEL authors="adnrey"

USER root

ARG ENV_FILE

ENV ENV_FILE=$ENV_FILE
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip "poetry==1.8.3"
RUN poetry config virtualenvs.create false --local
COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev

WORKDIR /src

COPY src .
