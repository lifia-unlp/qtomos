# Quantum State Tomography

Quantum State Tomography is the process of completely characterizing the quantum state of a system by performing a series of measurements on identical copies of the state. It allows us to mathematically reconstruct the density matrix, which fully describes the system.

Quantum State Tomography is generally a two-phase process:
1. **Data Acquisition**: Run quantum circuits on a simulator or real hardware to gather measurement statistics for a complete set of observables. In this toolset, we specifically use the complete set of tensor products of the non-identity Pauli matrices ($X, Y, Z$).
2. **State Reconstruction**: Use the acquired measurement data to mathematically reconstruct the density matrix of the quantum state.

> [!NOTE]
> This toolset is solely focused on **Data Acquisition (`qtomos`)**. State reconstruction is not handled by this repository.

Currently, data acquisition supports multiple predefined quantum states (GHZ, Phi+, W, and random circuits) defined in the `circuits_catalog`. You can dynamically select which circuit to prepare during acquisition.

This is now you basically use this tool:

```bash
# acquire data for the complete set of tensor products of the non-identity Pauli matrices (X, Y, Z), on the noiseless simulator, on a three qubit GHZ, using 500 shots for each measurement, saving the results to output.json
qtomos --circuit ghz --mode sim --shots 500 --file output.json
```

Read on to learn how to install and use this tool.

**IMPORTANT**: to connect to a real SpinQ QPU you need to provide your connection credentials. Read section "Acquire Data from the QPU" below. Do not put your access credentials in a file that is commited to the repository. 

---

# Install

SpinQit currently works only on Python 3.8. 

The file .python-version will most likely take care of setting up your environment with the correct Python version (if 3.8 is installed on your machine; if not, use pyenv, Conda or whatever manager you prefer to install it). 

We suggest installing everything in a virtual environment. 

To set up your environment, run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Arm based Macs, you'll have issues with the default location of SPinQit libraries. Use the ```fix-spinqit-macos-arm.sh```script to fix it (changes will only affect that venv)

---

## Data Acquisition

The first time you run `qtomos`, it may take longer (the SpinQ SDK might be downloading required assets).

### Simulate Acquisition

To run a simulation for a specific observable (e.g., `XX`) on a GHZ state:
```bash
qtomos --circuit ghz --mode sim --observable XX --file output.json
```

### Selecting a Circuit

You can select the quantum state to prepare using the `-c` or `--circuit` argument. The CLI dynamically exposes all circuits defined in `qtomos/circuits_catalog.py`. Current available states include `ghz` (default), `phi_plus`, `w`, and `random`.

```bash
# Acquire the ZZZ observable for a W state
qtomos --circuit w --mode sim --observable ZZZ --file output.json

# Acquire the full set for a random circuit
qtomos --circuit random --mode sim --file output.json
```

By default, the measurement bitstrings use Big-Endian format (qubit 0 is the leftmost bit). If you prefer Little-Endian (qubit 0 is the rightmost bit, similar to Qiskit), use the `--endian little` flag:
```bash
qtomos --circuit ghz --mode sim --observable XX --endian little --file output.json
```

### Acquire Data from the QPU

Before running on the real hardware (QPU), you need to configure your environment variables. 
Copy the `.env.example` file to `.env` and fill in your connection details:

```bash
cp .env.example .env
```

Edit `.env` to match your credentials:
```env
IP=192.168.172.233
PORT=50177
USERNAME=your_username
PASSWORD=your_password
```

Then, to acquire data for the same specific observable on the real hardware:
```bash
qtomos --circuit ghz --mode qpu --observable XX --file output.json
```

### Drawing Circuits

To generate a visual representation of the quantum circuit instead of simulating it or running it on the QPU, use the `draw` mode. This will save a `.png` image of the circuit in your current directory (e.g., `XX_of_a_Ghz.png`):
```bash
qtomos --circuit ghz --mode draw --observable XX --file output.json
```

### Full Tomographic Acquisition

To perform a full tomographic acquisition (all observables), omit the `--observable` argument. This defaults to 3 qubits.

```bash
# 3-qubit full tomographic acquisition on simulator
qtomos --circuit ghz --mode sim --file output.json

# 3-qubit full tomographic acquisition on QPU
qtomos --circuit ghz --mode qpu --file output.json
```

### Parametrizing Shots

By default, execution uses `1024` shots. You can customize the number of shots using the `--shots` flag:

```bash
qtomos --circuit ghz --mode sim --file output.json --shots 500
```

### Saving Output and Format

The output JSON file has the following structure:

```json
{
  "metadata": {
    "circuit_name": "ghz",
    "qubits": 2,
    "mode": "sim",
    "shots": 500,
    "endian": "big",
    "timestamps": {
      "start": "2026-06-25T20:51:33.528965-03:00",
      "end": "2026-06-25T20:51:33.530752-03:00"
    }
  },
  "measurements": {
    "XX": {
      "timestamps": {
        "start": "2026-06-25T20:51:33.529028-03:00",
        "end": "2026-06-25T20:51:33.530740-03:00"
      },
      "counts": {
        "00": 250,
        "11": 250
      },
      "qasm": "...",
      "native": "..."
    },
    ...
  }
}
```

### Help (qtomos)

For a complete list of options, use the `--help` flag:

```bash
$ qtomos --help
usage: qtomos [-h] [-m {sim,qpu,draw}] [-c {ghz,phi_plus,random,w}]
                  [-q QUBITS] [-e {big,little}] [--shots SHOTS] -f FILE
                  [-o OBSERVABLE]

Acquire SpinQ Tomographic Data

optional arguments:
  -h, --help            show this help message and exit
  -m {sim,qpu,draw}, --mode {sim,qpu,draw}
                        Execution mode: sim (simulator), qpu (real computer),
                        or draw (print circuit)
  -c {ghz,phi_plus,random,w}, --circuit {ghz,phi_plus,random,w}
                        Circuit to prepare
  -q QUBITS, --qubits QUBITS
                        Number of qubits (inferred from observable if omitted,
                        defaults to 3)
  -e {big,little}, --endian {big,little}
                        Endianness for output bitstrings: big (q[0] is
                        leftmost) or little (q[0] is rightmost)
  --shots SHOTS         Number of shots for execution
  -f FILE, --file FILE  Output JSON file path
  -o OBSERVABLE, --observable OBSERVABLE
                        Measure a single observable (e.g., XX, XYZ)
```


## Project Structure

The codebase is structured as follows:

*   **`pyproject.toml`**: The package configuration file defining dependencies and the CLI entry point.
*   **`qtomos/`**: Directory containing the project's internal modules and CLI:
    *   **`qtomos/__init__.py`**: Initializer that exposes `qtomos` as a Python package.
    *   **`qtomos/cli.py`**: CLI entry-point script for data acquisition. It handles argument parsing (simulator, real QPU, or circuit drawing, shots, endianness) and prints the structured JSON output with metadata.
    *   **`qtomos/acquisition.py`**: Contains the core logic and programmatic API (`measure_observable` and `measure_all_observables`) for executing the quantum circuits and gathering measurement statistics.
    *   **`qtomos/circuits_catalog.py`**: A catalog of pre-defined quantum circuits. The CLI dynamically discovers states defined here (e.g., `ghz`, `phi_plus`, `w`, `random`).
    *   **`qtomos/utils.py`**: Contains all shared mathematical utilities, including Pauli basis generation, match filtering, and average expectation calculation for marginal operators.
*   **`tests/`**: Directory for automated tests:
    *   **`tests/test_tomography.py`**: Unit test suite to validate supporting mathematical operations.

---

## Running Unit Tests

To run the automated unit tests and verify the consistency of the project, execute the following command from the repository root:

```bash
python tests/test_tomography.py
```
