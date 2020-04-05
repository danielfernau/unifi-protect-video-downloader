FROM python:3.8-slim as base

RUN mkdir /install
WORKDIR /install

COPY ./dist/*.whl /install/

RUN pip install *.whl

ENTRYPOINT [ "protect-archiver" ]
CMD [ "--help" ]

VOLUME [ "/downloads" ]
