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

# First check

The first time you run it, it may take longer (maybe spinq is downloading something else?)

## Simulate Acquisition

To run a simulation for a specific observable (e.g., `XX`):
```bash
python acquire.py --mode sim --single XX
```

By default, the measurement bitstrings use Big-Endian format (qubit 0 is the leftmost bit). If you prefer Little-Endian (qubit 0 is the rightmost bit, similar to Qiskit), use the `--endian little` flag:
```bash
python acquire.py --mode sim --single XX --endian little
```

## Acquire Data from the QPU

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

## Drawing Circuits

To generate a visual representation of the quantum circuit instead of simulating it or running it on the QPU, use the `draw` mode. This will save a `.png` image of the circuit in your current directory (e.g., `XX_of_a_Ghz.png`):
```bash
python acquire.py --mode draw --single XX
```

## Full Tomographic Acquisition

To perform a full tomographic acquisition (all observables), specify the number of qubits using the `--full` argument (defaults to 3 if omitted):

```bash
# 2-qubit full tomographic acquisition on simulator
python acquire.py --mode sim --full 2

# 3-qubit full tomographic acquisition on QPU
python acquire.py --mode qpu --full 3
```

## Saving Output to a File

Since the script outputs standard JSON, you can easily save the results of a full acquisition (or a single observable) to a file by redirecting standard output:

```bash
# Save 3-qubit full tomographic acquisition on QPU to a file
python acquire.py --mode qpu --full 3 > qpu_results_3q.json
```

## Help

For a complete list of options, use the `--help` flag:

```bash
$ python acquire.py --help
usage: acquire.py [-h] [-m {sim,qpu,draw}] [-e {big,little}] [-f {2,3} | -s SINGLE]

Acquire SpinQ Tomographic Data

optional arguments:
  -h, --help            show this help message and exit
  -m {sim,qpu,draw}, --mode {sim,qpu,draw}
                        Execution mode: sim (simulator), qpu (real computer), or draw (print circuit)
  -e {big,little}, --endian {big,little}
                        Endianness for output bitstrings: big (q[0] is leftmost) or little (q[0] is rightmost)
  -f {2,3}, --full {2,3}
                        Number of qubits for full tomography (2 or 3)
  -s SINGLE, --single SINGLE
                        Measure a single observable (e.g., XX, XYZ)
```
