NAME   := unifitoolbox/protect-archiver
TAG    := `git log -1 --pretty=%H`
IMG    := ${NAME}:${TAG}
LATEST := ${NAME}:latest

all: build push

build:
	@docker build -t ${IMG} .
	@docker tag ${IMG} ${LATEST}

push:
	@docker push ${NAME}
