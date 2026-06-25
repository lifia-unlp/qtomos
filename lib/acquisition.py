# lib/acquisition.py

from lib.ghz import Ghz
from spinqit import NMRConfig, get_basic_simulator, get_compiler, BasicSimulatorConfig, get_nmr, draw as sq_draw
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

TWO_QUBIT_OBSERVABLES = [
    "XX", "XY", "XZ",
    "YX", "YY", "YZ",
    "ZX", "ZY", "ZZ",
]

THREE_QUBIT_OBSERVABLES = [
    "XXX", "XXY", "XXZ",
    "XYX", "XYY", "XYZ",
    "XZX", "XZY", "XZZ",

    "YXX", "YXY", "YXZ",
    "YYX", "YYY", "YYZ",
    "YZX", "YZY", "YZZ",

    "ZXX", "ZXY", "ZXZ",
    "ZYX", "ZYY", "ZYZ",
    "ZZX", "ZZY", "ZZZ",
]

def simulate(c: Ghz, shots: int = 1024):
    comp = get_compiler("native")
    engine = get_basic_simulator()
    # Compile
    optimization_level = 0
    exe = comp.compile(c, optimization_level)
    # Run
    config = BasicSimulatorConfig()
    config.configure_shots(shots)
    result = engine.execute(exe, config)
    return result.counts

def run(c: Ghz, shots: int = 1024):
    IP = os.environ.get("IP")
    PORT = int(os.environ.get("PORT"))
    USERNAME = os.environ.get("USERNAME")        
    PASSWORD = os.environ.get("PASSWORD")
        
    comp = get_compiler("native")
    optimization_level = 0
    exe = comp.compile(c, optimization_level)   
    engine = get_nmr()
    config = NMRConfig()
    config.configure_ip(IP)
    config.configure_port(PORT)
    config.configure_account(USERNAME, PASSWORD)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    task_name = c.name
    task_desc = f"Execution of {c.name} at {timestamp}"
    config.configure_task(task_name, task_desc)
    config.configure_shots(shots) 
    resultado = engine.execute(exe, config)
    return resultado.counts

def draw(c: Ghz):
    compiler = get_compiler('native')
    ir = compiler.compile(c, level=0)
    filename = f"{c.name.replace(' ', '_')}.png"
    sq_draw(ir, filename=filename)
    print(f"Circuit drawing saved to {filename}")

def normalize_counts(counts, endian="big"):
    return {
        str(bitstring) if endian == "big" else str(bitstring)[::-1]: int(count)
        for bitstring, count in counts.items()
    }

def measure_observable(observable, mode, endian="big", shots: int = 1024):
    c: Ghz = Ghz(len(observable), f"{observable} of a Ghz")
    c.prepare_ghz_observation(observable)
    if mode == "draw":
        draw(c)
        return {observable: {}}
    elif mode == "qpu":
        counts = run(c, shots)
    else:
        counts = simulate(c, shots)
    return {observable: normalize_counts(counts, endian)}

def full(mode, full_qubits, endian="big", shots: int = 1024):
    results = {}
    observables = TWO_QUBIT_OBSERVABLES if full_qubits == 2 else THREE_QUBIT_OBSERVABLES
    for observable in observables:
        results.update(measure_observable(observable, mode, endian, shots))
    return results

def acquire_tomography_data(mode, single=None, full_qubits=None, endian="big", shots=1024):
    """
    Acquires tomography data for either a single observable or a full set.
    Returns a dictionary containing the measurements and execution metadata.
    """
    start_time = datetime.datetime.now().astimezone().isoformat()
    if single:
        measurements = measure_observable(single, mode, endian, shots)
        qubits = len(single)
    else:
        qubits = full_qubits if full_qubits is not None else 3
        measurements = full(mode, qubits, endian, shots)
    end_time = datetime.datetime.now().astimezone().isoformat()

    return {
        "metadata": {
            "state": Ghz.__name__,
            "qubits": qubits,
            "endian": endian,
            "shots": shots,
            "start-timestamp": start_time,
            "end-timestamp": end_time
        },
        "measurements": measurements
    }
