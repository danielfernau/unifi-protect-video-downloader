FROM --platform=$BUILDPLATFORM python:3.14-alpine AS build

RUN mkdir /build
WORKDIR /build

COPY . /build/

RUN python -m pip install --no-cache-dir -U poetry==2.3.3

RUN poetry build -f wheel --no-ansi --no-interaction


FROM python:3.14-alpine AS base

RUN mkdir /install

WORKDIR /install

COPY --from=build /build/dist/*.whl /install/

RUN pip install *.whl

ENTRYPOINT [ "protect-archiver" ]
CMD [ "--help" ]

VOLUME [ "/downloads" ]
