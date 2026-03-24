IMAGE_NAME ?= gest
IMAGE_TAG ?= latest

.PHONY: docker-build test lint

docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .
	uv run ty check
