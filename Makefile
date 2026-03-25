.PHONY: install dev test lint fmt clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

lint:
	ruff check src/ tests/

fmt:
	ruff format src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
