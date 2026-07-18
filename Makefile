.PHONY: install test plots clean

install:
	python -m pip install --upgrade pip
	pip install -e .[dev]

test:
	pytest

plots:
	python examples/01_basic_event.py
	python examples/02_compare_planet_masses.py
	python examples/03_noisy_observation.py
	python examples/04_compare_impact_parameters.py

clean:
	rm -rf __pycache__ src/roguelens/__pycache__ tests/__pycache__ .pytest_cache *.egg-info build dist
