# Quantum State Tomography

Quantum State Tomography is the process of completely characterizing the quantum state of a system by performing a series of measurements on identical copies of the state. It allows us to mathematically reconstruct the density matrix, which fully describes the system.

Quantum State Tomography is generally a two-phase process:
1. **Data Acquisition**: Run quantum circuits on a simulator or real hardware to gather measurement statistics for a complete set of observables. In this toolset, we specifically use the complete set of tensor products of the non-identity Pauli matrices ($X, Y, Z$).
2. **State Reconstruction**: Use the acquired measurement data to mathematically reconstruct the density matrix of the quantum state.

> [!NOTE]
> This toolset is solely focused on **Data Acquisition (`acquire.py`)**. State reconstruction is not handled by this repository.

Currently, data acquisition is configured for the GHZ (Greenberger-Horne-Zeilinger) state of 2 and 3 qubits. Future versions of this toolset will support other well-known quantum states.

This is now you basically use this tool:

```bash
# acquire data for the complete set of tensor products of the non-identity Pauli matrices (X, Y, Z), on the noiseless simulator, on a three qubit GHZ, using 500 shots for each measurement, sending the results to the standard output
python acquire.py --mode sim --full 3 --shots 500
```

Read on to learn how to install and use this tool.

**IMPORTANT**: to connect to a real SpinQ QPU you need to provide your connection credentials. Read section "Acquire Data from the QPU" below. Do not put your access credentials in a file that is commited to the repository. 

---

# Install

SpinQit currently works only on Python 3.8. 

The file .python-version will most likely take care of setting up your environment with the correct Python version (if 3.8 is installed on your machine; if not, use pyenv, Conda or whatever manager you prefer to install it). 

We suggest installing everything in a virtual environment. 

To set up your environment, run:

```python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Arm based Macs, you'll have issues with the default location of SPinQit libraries. Use the ```fix-spinqit-macos-arm.sh```script to fix it (changes will only affect that venv)

---

## Data Acquisition

The first time you run `acquire.py`, it may take longer (the SpinQ SDK might be downloading required assets).

### Simulate Acquisition

To run a simulation for a specific observable (e.g., `XX`):
```bash
python acquire.py --mode sim --single XX
```

By default, the measurement bitstrings use Big-Endian format (qubit 0 is the leftmost bit). If you prefer Little-Endian (qubit 0 is the rightmost bit, similar to Qiskit), use the `--endian little` flag:
```bash
python acquire.py --mode sim --single XX --endian little
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
python acquire.py --mode qpu --single XX
```

### Drawing Circuits

To generate a visual representation of the quantum circuit instead of simulating it or running it on the QPU, use the `draw` mode. This will save a `.png` image of the circuit in your current directory (e.g., `XX_of_a_Ghz.png`):
```bash
python acquire.py --mode draw --single XX
```

### Full Tomographic Acquisition

To perform a full tomographic acquisition (all observables), specify the number of qubits using the `--full` argument (defaults to 3 if omitted):

```bash
# 2-qubit full tomographic acquisition on simulator
python acquire.py --mode sim --full 2

# 3-qubit full tomographic acquisition on QPU
python acquire.py --mode qpu --full 3
```

### Parametrizing Shots

By default, execution uses `1024` shots. You can customize the number of shots using the `--shots` flag:

```bash
python acquire.py --mode sim --full 2 --shots 500
```

### Saving Output and Format

Since the script outputs standard JSON, you can easily save the results to a file by redirecting standard output:

```bash
# Save 3-qubit full tomographic acquisition on QPU to a file
python acquire.py --mode qpu --full 3 > qpu_results_3q.json
```

The output JSON file has the following structure:

```json
{
  "metadata": {
    "state": "Ghz",
    "qubits": 2,
    "endian": "big",
    "shots": 500,
    "start-timestamp": "2026-06-20T22:07:15.649607-03:00",
    "end-timestamp": "2026-06-20T22:07:15.650332-03:00"
  },
  "measurements": {
    "XX": {
      "00": 250,
      "11": 250
    },
    "XY": {
      "00": 125,
      "01": 125,
      "10": 125,
      "11": 125
    },
    ...
  }
}
```

### Help (acquire.py)

For a complete list of options, use the `--help` flag:

```bash
$ python acquire.py --help
usage: acquire.py [-h] [-m {sim,qpu,draw}] [-e {big,little}] [--shots SHOTS]
                  [-f {2,3} | -s SINGLE]

Acquire SpinQ Tomographic Data

optional arguments:
  -h, --help            show this help message and exit
  -m {sim,qpu,draw}, --mode {sim,qpu,draw}
                        Execution mode: sim (simulator), qpu (real computer),
                        or draw (print circuit)
  -e {big,little}, --endian {big,little}
                        Endianness for output bitstrings: big (q[0] is
                        leftmost) or little (q[0] is rightmost)
  --shots SHOTS         Number of shots for execution
  -f {2,3}, --full {2,3}
                        Number of qubits for full tomography (2 or 3)
  -s SINGLE, --single SINGLE
                        Measure a single observable (e.g., XX, XYZ)
```


## Project Structure

The codebase is structured as follows:

*   **`acquire.py`**: CLI entry-point script for data acquisition. It handles argument parsing (simulator, real QPU, or circuit drawing, shots, endianness) and prints the structured JSON output with metadata.
*   **`lib/`**: Directory containing the project's internal modules:
    *   **`lib/__init__.py`**: Initializer that exposes `lib` as a Python package.
    *   **`lib/acquisition.py`**: Contains the core logic and programmatic API (`acquire_tomography_data`) for executing the quantum circuits and gathering measurement statistics.
    *   **`lib/circuits_catalog.py`**: A catalog of pre-defined quantum circuits. Currently defines the `Ghz` class, which specifies the GHZ state preparation circuit.
    *   **`lib/utils.py`**: Contains all shared mathematical utilities, including Pauli basis generation, match filtering, and average expectation calculation for marginal operators.
*   **`tests/`**: Directory for automated tests:
    *   **`tests/test_tomography.py`**: Unit test suite to validate supporting mathematical operations.

---

## Running Unit Tests

To run the automated unit tests and verify the consistency of the project, execute the following command from the repository root:

```bash
python tests/test_tomography.py
```
