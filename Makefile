PYTHON := .venv/bin/python
SRC := src
export PYTHONPATH := src/pets
export MYPYPATH := src/pets

.PHONY: install lint typecheck check run

install:
	$(PYTHON) -m pip install -r requirements.txt

lint:
	$(PYTHON) -m flake8 $(SRC)

typecheck:
	$(PYTHON) -m mypy --strict --explicit-package-bases $(SRC)/pets

check: lint typecheck

run:
	PYTHONPATH=src/pets .venv/bin/python src/pets/__main__.py
