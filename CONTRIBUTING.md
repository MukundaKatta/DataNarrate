# Contributing to DataNarrate

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/MukundaKatta/DataNarrate.git
cd DataNarrate
pip install -e ".[dev]"
```

## Running Tests

```bash
make test
```

## Linting

```bash
make lint
```

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Write tests for new functionality.
3. Ensure all tests pass and linting is clean.
4. Open a PR against `main` with a clear description.

## Adding a New Narrator

1. Create a class in `src/datanarrate/core.py` following the existing pattern.
2. Add templates in `src/datanarrate/config.py` for all three tones.
3. Wire the narrator into `DataStoryteller.tell_story()`.
4. Add tests in `tests/test_core.py`.

## Code Style

- Follow PEP 8 conventions; we enforce via **ruff**.
- Use type hints for all public APIs.
- Keep functions focused and well-documented.
