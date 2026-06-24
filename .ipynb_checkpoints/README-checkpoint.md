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

# Quantum State Tomography Workflow

Quantum State Tomography with this toolset is a two-phase process:
1. **Data Acquisition (`acquire.py`)**: Run quantum circuits on a simulator or the real SpinQ hardware to gather measurement statistics for a complete set of Pauli observables.
2. **State Reconstruction (`reconstruct.py`)**: Use the acquired measurement data to mathematically reconstruct the density matrix of the quantum state.

Currently, data acquisition and reconstruction are configured for the GHZ (Greenberger-Horne-Zeilinger) state of 2 and 3 qubits. Future versions of this toolset will support other well-known quantum states.

---

## Phase 1: Data Acquisition

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

---

## Phase 2: State Reconstruction

After acquiring the JSON data, use `reconstruct.py` to reconstruct the density matrix of the state.

### Basic Usage

You can reconstruct the state using either Maximum Likelihood Estimation (MLE) or Linear Inversion (linear). By default, MLE is used. Since the JSON output of `acquire.py` contains all the execution metadata, `reconstruct.py` automatically reads the number of qubits and the endianness from the file, meaning you do not need to specify them as parameters:

```bash
# Reconstruct using the default MLE method
python reconstruct.py --file qpu_results_3q.json

# Reconstruct using the Linear Inversion method
python reconstruct.py --file qpu_results_3q.json --method linear
```

### Marginal Operator Estimation and Averaging

To perform a complete reconstruction using linear inversion or MLE over the Pauli basis, `reconstruct.py` needs to estimate the expectation value of all $4^N$ possible operators (including those containing the identity operator `I`, such as `XI` or `IZZ`).

Since `acquire.py` only performs measurements on complete observables (without `I`), the marginal expectation values are extracted from these complete measurements by ignoring the qubits where the identity acts. For instance, the expectation of the marginal `ZI` for 2 qubits can be extracted from measurements of the complete observables `ZX`, `ZY`, or `ZZ`. To maximize statistical precision and reduce estimator variance, `reconstruct.py` finds all complete measurements compatible with a given marginal and computes the arithmetic mean of their individual expectation values.

### Plotting

To visualize the reconstructed density matrix as a 3D "Cityscape" bar chart (showing real and imaginary parts), append the `--plot` flag:
```bash
python reconstruct.py --file qpu_results_3q.json --plot
```

### Help (reconstruct.py)

For a complete list of options:

```bash
$ python reconstruct.py --help
usage: reconstruct.py [-h] -f FILE [-m {linear,mle}] [-p]

State Reconstruction for SpinQ Tomography

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Input JSON file containing measurement counts
  -m {linear,mle}, --method {linear,mle}
                        Reconstruction method (linear or mle)
  -p, --plot            Plot the density matrix cityscape
```

---

## Project Structure

The codebase is structured as follows:

*   **`acquire.py`**: Entry-point script for the data acquisition phase. It configures the execution options (simulator, real QPU, or circuit drawing), the number of shots (`--shots`), and the endianness, printing the structured JSON output with metadata.
*   **`reconstruct.py`**: Entry-point script for quantum state reconstruction. It loads the data generated by `acquire.py` and delegates the reconstruction to the selected algorithm using the *Strategy* pattern.
*   **`lib/`**: Directory containing the project's internal modules:
    *   **`lib/__init__.py`**: Initializer that exposes `lib` as a Python package.
    *   **`lib/ghz.py`**: Defines the `Ghz` class, which specifies the GHZ state preparation circuit, measurement basis changes, and its ideal theoretical density matrix representation.
    *   **`lib/reconstruction_strategy.py`**: Defines the abstract `ReconstructionStrategy` interface that all reconstruction methods must implement.
    *   **`lib/linear_inversion.py`**: Implements the reconstruction strategy using linear inversion of Pauli operators.
    *   **`lib/mle_least_squares.py`**: Implements the reconstruction strategy using constrained weighted least squares (MLE based on Cholesky).
    *   **`lib/utils.py`**: Contains all shared mathematical utilities, including Pauli basis generation, match filtering, and average expectation calculation for marginal operators.
*   **`tests/`**: Directory for automated tests:
    *   **`tests/test_tomography.py`**: Unit test suite to validate supporting mathematical operations and the integrity of the state reconstruction strategies.

---

## Running Unit Tests

To run the automated unit tests and verify the consistency of the project, execute the following command from the repository root:

```bash
python tests/test_tomography.py
```
