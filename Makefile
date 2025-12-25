.PHONY: test lint format install

install:
	uv sync

test:
	uv run pytest -q

lint:
	uv run ruff check .
	uv run black . --check

format:
	uv run ruff format .
	uv run black .
