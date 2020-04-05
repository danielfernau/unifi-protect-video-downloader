NAME   := unifitoolbox/protect-archiver
TAG    := `git log -1 --pretty=%H`
IMG    := ${NAME}:${TAG}
LATEST := ${NAME}:latest

build:
	@rm -rf ./dist
	@poetry build -f wheel --no-ansi --no-interaction
	@docker build -t ${IMG} .
	@docker tag ${IMG} ${LATEST}

push:
	@docker push ${NAME}
