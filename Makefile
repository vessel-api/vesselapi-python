.PHONY: all lint typecheck test fmt install smoke

all: fmt lint typecheck test

lint:
	ruff check src/ tests/

typecheck:
	mypy src/vessel_api_python/

test:
	pytest -v tests/

fmt:
	ruff format src/ tests/

install:
	pip install -e ".[dev]"

smoke:
	pytest -v -m smoke tests/
