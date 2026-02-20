ROOT_DIR := ../..

.DEFAULT_GOAL := run

.PHONY: run setup test lint format root-%

run:
	uv run python -m src

setup:
	uv sync

test:
	uv run pytest

lint:
	$(MAKE) -C $(ROOT_DIR) lint

format:
	$(MAKE) -C $(ROOT_DIR) format

root-%:
	$(MAKE) -C $(ROOT_DIR) $*
