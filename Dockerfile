FROM zapier/python:latest as base

RUN mkdir /build
WORKDIR /build

COPY . /build/

RUN poetry install --no-interaction --no-ansi
RUN ln -s $(poetry env info -p)/bin/protect-archiver /usr/local/bin/protect-archiver

ENTRYPOINT [ "protect-archiver" ]
CMD [ "--help" ]

VOLUME [ "/downloads" ]
