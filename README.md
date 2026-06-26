# Quantum State Tomography (qtomos)

Quantum State Tomography is the process of completely characterizing the quantum state of a system by performing a series of measurements on identical copies of the state. It allows us to mathematically reconstruct the density matrix, which fully describes the system.

This toolset is specifically designed for **SpinQ NMR quantum computers** and has been successfully tested on the **Triangulum (3-qubit)** system.

Quantum State Tomography is generally a two-phase process:
1. **Data Acquisition**: Run quantum circuits on a simulator or real hardware to gather measurement statistics for a complete set of observables. In this toolset, we specifically use the complete set of tensor products of the non-identity Pauli matrices ($X, Y, Z$).
2. **State Reconstruction**: Use the acquired measurement data to mathematically reconstruct the density matrix of the quantum state.

> [!NOTE]
> This toolset is solely focused on **Data Acquisition (`qtomos`)**. State reconstruction is not handled by this repository.

## Features

- **Multi-backend support:** Run acquisitions seamlessly on a simulator (`sim`) or directly on actual quantum hardware (`qpu`).
- **Granular Control:** Measure single observables (e.g., `XX`) or effortlessly execute an automated sequence covering all permutations for full tomographic reconstruction.
- **Customizable Circuits:** Dynamically load pre-defined state preparation circuits (GHZ, Phi+, W, Random) from the catalog or define your own.
- **Structured JSON Output:** Measurements are paired with timestamps, counts, runtime configurations, and the compiled QASM logic.

## Quickstart

You can install `qtomos` directly from PyPI:
```bash
pip install qtomos
```

## Documentation

Depending on your use case, refer to the following dedicated guides:

- 📖 **[CLI Usage Guide](README-CLI.md)**: Learn how to perform tomography directly from your terminal using the `qtomos` command.
- 📓 **[Jupyter Notebook Guide](README-NOTEBOOK.md)**: Learn how to import and use the programmatic APIs within Python scripts and Jupyter Notebooks.
- 🛠️ **[Developer Guide](README-DEV.md)**: Learn how to set up the repository for local development, run tests, and understand the project structure.
