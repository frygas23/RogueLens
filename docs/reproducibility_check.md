# Reproducibility check

This file records the latest local check of the project.

## Commands run

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python examples/01_basic_event.py
PYTHONPATH=src python examples/02_compare_planet_masses.py
PYTHONPATH=src python examples/03_noisy_observation.py
PYTHONPATH=src python examples/04_compare_impact_parameters.py
PYTHONPATH=src python examples/05_export_event_report.py
PYTHONPATH=src python main.py --preset earth --output plots/cli_event.png --csv outputs/cli_event.csv --report outputs/cli_event_report.md
```

## Result

- Unit tests: **9 passed**
- Example plots generated successfully
- CSV export generated successfully
- Markdown report export generated successfully

## Interpretation

The project is reproducible from the repository root when `PYTHONPATH=src` is used or after installing with `pip install -e .`.
