.PHONY: install
install:
	poetry install

.PHONY: test
test:
	poetry run pytest

.PHONY: build
build:
	poetry build

.PHONY: build-check
build-check: build
	twine check dist/*

.PHONY: publish
publish: build
	poetry publish



