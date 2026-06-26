# Using `qtomos` Programmatically in Jupyter Notebooks

Because `qtomos` is a properly configured Python package, you can easily import its internals into your own Python scripts or Jupyter Notebooks.

## Installation

Ensure the package is installed in your Notebook's environment:
```bash
!pip install qtomos
```

## Basic Tomography Acquisition

You can access the core API methods directly from the package. Here's a complete example of generating a state, running a full tomographic acquisition sequence on the simulator, and analyzing the raw results in Python:

```python
from qtomos import measure_all_observables, circuits_catalog
import json

# 1. Prepare the quantum circuit using the predefined catalog
# Example: 3-qubit GHZ state
circuit = circuits_catalog.create_ghz(3)

# 2. Acquire all observables for full tomography
results = measure_all_observables(
    circuit=circuit,
    mode="sim",         # Use "sim", "qpu", or "draw"
    endian="big",       # Big-endian configuration
    shots=1024
)

# 3. Analyze the results
measurements = results["measurements"]
print(f"Total Observables Measured: {len(measurements)}")
print(json.dumps(measurements["XXZ"], indent=2))
```

### Parameters for `measure_all_observables`
- `circuit` (*spinqit.Circuit*): The quantum circuit to execute. The number of allocated qubits will determine the complete Pauli basis (2 or 3 qubits).
- `mode` (*str*): The execution backend. Can be `"sim"` (local noiseless simulator), `"qpu"` (SpinQ real hardware), or `"draw"` (outputs a PNG of the circuit without running).
- `endian` (*str, optional*): Defines the order of qubits in the measurement bitstrings. `"big"` (default, q[0] is leftmost) or `"little"` (q[0] is rightmost, similar to Qiskit).
- `shots` (*int, optional*): Number of execution shots. Defaults to `1024`.

## Measuring a Single Observable

If you don't need a full tomography run, you can utilize `measure_observable` instead:

```python
from qtomos import measure_observable, circuits_catalog

# Prepare a 2-qubit Phi+ Bell State
circuit = circuits_catalog.create_phi_plus(2)

# Measure ONLY the 'XY' observable
result = measure_observable(
    circuit=circuit,
    observable="XY",
    mode="sim",
    shots=500
)

print(result["XY"]["counts"])
```

### Parameters for `measure_observable`
- `circuit` (*spinqit.Circuit*): The quantum circuit to execute.
- `observable` (*str*): The specific Pauli observable to measure (e.g., `"XX"`, `"XYZ"`).
- `mode` (*str*): The execution backend (`"sim"`, `"qpu"`, or `"draw"`).
- `endian` (*str, optional*): Bitstring ordering (`"big"` or `"little"`). Defaults to `"big"`.
- `shots` (*int, optional*): Number of execution shots. Defaults to `1024`.

## Defining Custom Circuits Inline

You don't have to rely exclusively on the predefined catalog. You can define your own `spinqit` circuits right inside your notebook and pass them directly to `qtomos` for data acquisition!

```python
from qtomos import measure_all_observables
from spinqit import Circuit, H, CX

# 1. Define a custom circuit manually
circuit = Circuit()
circuit.allocateQubits(2)
circuit << (H, 0)
circuit << (CX, [0, 1])

# 2. Run tomography on your custom circuit
results = measure_all_observables(circuit, mode="sim")
print(results["measurements"]["XX"]["counts"])
```

## Connecting to the QPU

When using `mode="qpu"` within a Notebook, ensure you have correctly set the environment variables in your active shell or load them directly using `python-dotenv`:

```python
import os
from dotenv import load_dotenv

load_dotenv() # Assumes a .env file is present in the notebook directory

os.environ["IP"] = "192.168.172.233"
os.environ["PORT"] = "50177"
os.environ["USERNAME"] = "your_username"
os.environ["PASSWORD"] = "your_password"

# Now measure against the real hardware
results = measure_all_observables(circuit, mode="qpu")
```
