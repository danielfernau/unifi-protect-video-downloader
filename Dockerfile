FROM python:3.8.1-alpine as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME=/poetry \
    POETRY_VERSION=1.0.3

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM base as builder
RUN mkdir /install
WORKDIR /install

RUN apk add --no-cache curl python3-dev openssl-dev libffi-dev musl-dev gcc

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /install/
# HACK(dcramer): we need the module to be installable at this stage
RUN mkdir protect_archiver && touch protect_archiver/__init__.py
RUN poetry install --no-interaction --no-ansi

# TODO:
# FROM base
# COPY --from=builder /install /usr/local
# COPY --from=builder $POETRY_HOME $POETRY_HOME
COPY . /install/

# WORKDIR /app

# ensure we've got full module install now
RUN poetry install --no-interaction --no-ansi

ENTRYPOINT [ "protect-archiver" ]
