ARG PYTHON_IMAGE_VARIANT="3.11"
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_IMAGE_VARIANT}

# update path to include user's .local/bin
ENV PATH="${PATH}:/home/vscode/.local/bin"

# set workdir
WORKDIR /IdeaProjects/unifi-protect-video-downloader

# Poetry
ARG POETRY_VERSION="1.7.0"
#RUN su vscode -c "umask 0002 && pip3 --disable-pip-version-check install poetry==${POETRY_VERSION}"
#RUN su vscode -c "umask 0002 && poetry install"

# Nox
#ARG NOX_VERSION="none"
#RUN if [ "${NOX_VERSION}" != "none" ]; then su vscode -c "umask 0002 && pip3 install nox-poetry nox==${NOX_VERSION}"; fi

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1
