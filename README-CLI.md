# `acquire` Command-Line Interface (CLI) Guide

The `acquire` CLI is the primary way to interact with the data acquisition toolset from your terminal.

> The first time you run `acquire`, it may take longer as the SpinQ SDK might be downloading required assets.

## Basic Usage

The CLI requires you to specify the `--circuit` and the `--mode` explicitly for every run.
The output file (`--file` or `-f`) is optional. If omitted, a filename will be automatically generated for you.

```bash
acquire --circuit ghz --mode sim
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
acquire --circuit w --mode sim

# Acquire a full tomography for a random state (with explicit output file)
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
QTOMOS_IP=ip-of-your-spinquasar-server
QTOMOS_PORT=port-of-your-spinquasar-server
QTOMOS_USERNAME=your_username
QTOMOS_PASSWORD=your_password
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

## Output Format & Auto-naming

The `--file` flag defines where the output JSON is saved. 

**Auto-naming**: If you omit the `--file` flag, the CLI will automatically generate a filename in the current directory using the following pattern:
`[circuit_name]-[qubits]-[mode]-run_[N].json`

Where `[N]` is an incrementing integer starting from 1. For example, if you run a 3-qubit GHZ circuit in simulator mode, it will generate `ghz-3-sim-run_1.json`. If that file already exists, it will use `ghz-3-sim-run_2.json`, and so on.

The output JSON has the following structure:

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
