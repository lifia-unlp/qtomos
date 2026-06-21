# Install

SpinQit currently works only on Python 3.8. 

The file .python-version will most likely take care of setting up your environment with the correct Python version (if 3.8 is installed on your machine; if not, use pyenv, Conda or wathever manager you preffer to install it). 

We suggest install everything in a virtual environment. 

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

You can reconstruct the state using the default Maximum Likelihood Estimation (MLE) method. Since the JSON output of `acquire.py` contains all the execution metadata, `reconstruct.py` automatically reads the number of qubits and the endianness from the file, meaning you do not need to specify them as parameters:

```bash
python reconstruct.py --file qpu_results_3q.json
```

### Estimación de Operadores Marginales y Promediado

Para realizar una reconstrucción completa por mínimos cuadrados o MLE sobre la base de operadores de Pauli, `reconstruct.py` requiere estimar el valor de expectación de los $4^N$ operadores posibles (incluyendo aquellos que contienen el operador de identidad `I`, como `XI` o `IZZ`). 

Dado que `acquire.py` solo realiza mediciones sobre los observables completos (sin `I`), los valores de expectación marginales se extraen a partir de estas mediciones completas ignorando los qubits en donde actúa la identidad. Por ejemplo, la expectación del marginal `ZI` para 2 qubits se puede extraer de las mediciones de los observables completos `ZX`, `ZY` o `ZZ`. Para maximizar la precisión estadística y reducir la varianza del estimador, `reconstruct.py` busca todas las mediciones completas compatibles con un marginal determinado y calcula la media aritmética de sus valores de expectación individuales.

### Methods

You can choose between `linear` (Linear Inversion) or `mle` (Maximum Likelihood Estimation) using the `--method` flag:
```bash
python reconstruct.py --file qpu_results_3q.json --method linear
```

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

## Estructura del Proyecto

El código está estructurado de la siguiente manera:

*   **`acquire.py`**: Script de entrada para la fase de adquisición. Configura las opciones de ejecución (simulador, QPU real o graficado de circuitos), la cantidad de disparos (`--shots`) y la endianness, imprimiendo el resultado JSON estructurado con metadatos.
*   **`reconstruct.py`**: Script de entrada para la reconstrucción del estado cuántico. Carga los datos generados por `acquire.py` y delega la ejecución de la reconstrucción al algoritmo seleccionado mediante el patrón *Strategy*.
*   **`lib/`**: Directorio contenedor de los módulos internos del proyecto:
    *   **`lib/__init__.py`**: Inicializador que expone a `lib` como un paquete en Python.
    *   **`lib/smart_ghz.py`**: Define la clase `SmartGhz`, la cual especifica el circuito de preparación del estado GHZ y los cambios de base de medición.
    *   **`lib/reconstruction_strategy.py`**: Define la interfaz abstracta `ReconstructionStrategy` que deben implementar todos los métodos de reconstrucción.
    *   **`lib/linear_inversion.py`**: Implementa la estrategia de reconstrucción mediante inversión lineal de operadores de Pauli.
    *   **`lib/mle_least_squares.py`**: Implementa la estrategia de reconstrucción mediante mínimos cuadrados ponderados restringidos (MLE basado en Cholesky).
    *   **`lib/utils.py`**: Contiene todas las funciones matemáticas compartidas, incluyendo la generación de la base de Pauli, filtros de coincidencia y el cálculo promedio de expectaciones para operadores marginales.
*   **`tests/`**: Directorio de pruebas automatizadas:
    *   **`tests/test_tomography.py`**: Suite de pruebas unitarias para validar las operaciones matemáticas de soporte y la integridad de las estrategias de reconstrucción de estado.

---

## Ejecución de Pruebas Unitarias

Para correr las pruebas unitarias automatizadas y verificar la consistencia del proyecto, ejecuta el siguiente comando desde la raíz del repositorio:

```bash
python tests/test_tomography.py
```
