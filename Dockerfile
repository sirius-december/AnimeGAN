FROM python:3.12.8-slim-bookworm

ENV POETRY_VERSION=1.8.5

RUN apt update && apt upgrade -y && apt install -y curl

RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-interaction --no-ansi

COPY . /app/

ENTRYPOINT ["poetry", "run", "python", "AnimeGAN/main.py"]