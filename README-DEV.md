# `qtomos` Developer Guide

This document outlines how to set up your local environment to contribute to the `qtomos` repository, run tests, and publish releases.

## Prerequisites

- macOS (Intel or Apple Silicon) / Linux / Windows
- Python 3.8 (SpinQit currently strictly requires Python 3.8)

## Local Setup

We highly suggest installing dependencies inside a Python virtual environment.
If you use `pyenv`, the existing `.python-version` file will automatically configure Python 3.8.

1. **Clone the repository:**
```bash
git clone git@github.com:lifia-unlp/qtomos.git
cd qtomos
```

2. **Initialize a Virtual Environment:**
```bash
python -m venv .venv
source .venv/bin/activate
```

3. **Install the Package for Development:**
Installing with the `-e` (editable) flag ensures that any changes you make to the source code are immediately reflected in your environment without needing to reinstall.
```bash
pip install -e .
```

### Apple Silicon (M-Series Mac) Fix
On Arm-based Macs, you'll encounter architecture issues with the default SpinQit C++ compiled libraries. We have provided a script to align the dynamically linked libraries. Run:
```bash
./fix-spinqit-macos-arm.sh
```
*(Note: These changes only modify the libraries within your active `.venv`)*

## Project Structure

*   **`pyproject.toml`**: The package configuration file defining metadata, dependencies, and the CLI entry point.
*   **`qtomos/`**: The core Python package:
    *   **`__init__.py`**: Exposes the programmatic APIs.
    *   **`cli.py`**: The entry-point script utilized by the `qtomos` terminal command.
    *   **`acquisition.py`**: Contains the core logic (`measure_observable` and `measure_all_observables`).
    *   **`circuits_catalog.py`**: A catalog of pre-defined quantum circuits (`ghz`, `phi_plus`, `w`, `random`). Add new circuits here!
    *   **`utils.py`**: Mathematical utilities, Pauli basis generators, and match filtering.
*   **`tests/`**: Directory for automated unit tests.

## Running Unit Tests

Automated tests reside in the `tests/` directory and validate the consistency of the mathematical algorithms. To run the tests, execute:

```bash
python -m unittest tests/test_tomography.py
```

## Adding New Circuits

To add a new state preparation sequence to the CLI:
1. Open `qtomos/circuits_catalog.py`.
2. Define a new function starting with `create_` (e.g., `create_bell(qubits: int) -> Circuit`).
3. Return the `spinqit.Circuit` instance.
4. The CLI (`qtomos/cli.py`) will automatically discover your function via introspection and expose it as `--circuit bell`.

## Publishing to PyPI

If you have write access to the GitHub repository, PyPI deployments are automated. 
Navigate to the GitHub Actions tab, select the **Publish to PyPI** workflow, and trigger a manual workflow run. GitHub's Trusted Publisher integration will securely handle the release.
