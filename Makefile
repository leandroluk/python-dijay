.DEFAULT_GOAL := setup

.PHONY: setup install test test-cov build publish clean lint format tag

setup:
	uv venv --python 3.14
	uv sync

install:
	uv sync

lint:
	uv run ruff check --fix .
	uv run ruff format --check .
	uv run mypy dijay

format:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

test-cov:
	uv run pytest --cov=dijay --cov-report=xml:coverage.xml

build:
	uv build

publish: build
	uv publish

clean:
	python -c "import shutil, pathlib; \
	[shutil.rmtree(p, ignore_errors=True) for p in ['dist', '.pytest_cache', '.venv']]; \
	[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; \
	[p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"

tag:
	@python -c "import sys; v='$(v)'; sys.exit('Usage: make tag v=X.Y.Z') if not v else None"
	@python -c "import re, pathlib; \
	p = pathlib.Path('pyproject.toml'); \
	p.write_text(re.sub(r'version = \".*?\"', 'version = \"$(v)\"', p.read_text(), count=1))"
	@git add pyproject.toml
	@git commit -m "chore: bump version to $(v)"
	@git tag v$(v)
	@git push --follow-tags
	@echo "Tagged v$(v)"