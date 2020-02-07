FROM python:3.8.1-alpine

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/0.12.16/get-poetry.py | python \
    && poetry config settings.virtualenvs.create false

COPY pyproject.toml poetry.lock /usr/src/app/
# HACK(dcramer): we need the atlas module to be installable at this stage
RUN mkdir unifi_protect && touch unifi_protect/__init__.py
RUN poetry install --no-dev

COPY . /usr/src/app/
# ensure we've got full module install now
RUN poetry install --no-dev

ENV PATH /usr/src/app/bin:$PATH

ENTRYPOINT [ "unifi-protect" ]
