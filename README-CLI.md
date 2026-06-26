# `acquire` Command-Line Interface (CLI) Guide

The `acquire` CLI is the primary way to interact with the data acquisition toolset from your terminal.

> The first time you run `acquire`, it may take longer as the SpinQ SDK might be downloading required assets.

## Basic Usage

The CLI requires you to specify the `--circuit` and the `--mode` explicitly for every run.

```bash
acquire --circuit ghz --mode sim --file output.json
```

## Execution Modes

The `--mode` flag determines where the quantum circuit will be executed:
- **`sim`**: Run the circuit on the local noiseless simulator.
- **`qpu`**: Run the circuit on the actual SpinQ quantum hardware.
- **`draw`**: Do not run the circuit; instead, generate a `.png` image of the circuit in the current directory.

## Selecting a Circuit

You can select the quantum state to prepare using the `--circuit` argument. The CLI dynamically exposes all circuits defined in `qtomos/circuits_catalog.py`. 

Available predefined states include: `ghz`, `phi_plus`, `w`, and `random`.

```bash
# Acquire a full tomography for a W state
acquire --circuit w --mode sim --file output.json

# Acquire a full tomography for a random state
acquire --circuit random --mode sim --file output.json
```

## Measuring Specific Observables

By default, the CLI performs a **full tomographic acquisition**, meaning it automatically generates and measures all possible combinations of X, Y, and Z observables for the circuit's qubits.

To measure only a single specific observable (e.g., `XX`), use the `--observable` flag:
```bash
acquire --circuit ghz --mode sim --observable XX --file output.json
```

## Connecting to the QPU

Before running on the real hardware (`--mode qpu`), you need to configure your environment variables with your connection credentials. 

Create a `.env` file in the directory where you are running the command:
```env
IP=192.168.172.233
PORT=50177
USERNAME=your_username
PASSWORD=your_password
```

Then, execute the command:
```bash
acquire --circuit ghz --mode qpu --file output.json
```
**IMPORTANT**: Do not commit your `.env` file containing real credentials to version control.

## Additional Parameters

### Shots
By default, execution uses `1024` shots. You can customize the number of shots using the `--shots` flag:
```bash
acquire --circuit ghz --mode sim --file output.json --shots 500
```

### Endianness
By default, the measurement bitstrings use Big-Endian format (qubit 0 is the leftmost bit). If you prefer Little-Endian (qubit 0 is the rightmost bit, typical in IBM Qiskit), use the `--endian little` flag:
```bash
acquire --circuit ghz --mode sim --observable XX --endian little --file output.json
```

## Output Format

The `--file` flag defines where the output JSON is saved. It has the following structure:

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

## Help Menu

For a complete list of options, use the `--help` flag:
```bash
$ acquire --help
```
