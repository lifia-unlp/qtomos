from SmartGhz import SmartGhz
from spinqit import NMRConfig, get_basic_simulator, get_compiler, BasicSimulatorConfig, get_nmr, draw as sq_draw

import json
import argparse
import os
import datetime

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

def simulate(c: SmartGhz) :
    comp = get_compiler("native")
    engine = get_basic_simulator()
    # Compile
    optimization_level = 0
    exe = comp.compile(c, optimization_level)
    # Run
    config = BasicSimulatorConfig()
    config.configure_shots(1024)
    result = engine.execute(exe, config)
    return result.counts

def run(c: SmartGhz):
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
    config.configure_shots(1024) 
    resultado = engine.execute(exe, config)
    return resultado.counts

def draw(c: SmartGhz):
    compiler = get_compiler('native')
    ir = compiler.compile(c, level=0)
    filename = f"{c.name.replace(' ', '_')}.png"
    sq_draw(ir, filename=filename)
    print(f"Circuit drawing saved to {filename}")

def normalize_counts(counts):
    return {
        str(bitstring): int(count)
        for bitstring, count in counts.items()
    }

def measure_observable(observable, mode):
    c: SmartGhz = SmartGhz(len(observable), f"{observable} of a Ghz")
    c.prepare_ghz_observation(observable)
    if mode == "draw":
        draw(c)
        return {observable: {}}
    elif mode == "qpu":
        counts = run(c)
    else:
        counts = simulate(c)
    return {observable: normalize_counts(counts)}

def full(mode, full_qubits):
    results = {}
    observables = TWO_QUBIT_OBSERVABLES if full_qubits == 2 else THREE_QUBIT_OBSERVABLES
    for observable in observables:
        results.update(measure_observable(observable, mode))
    print(json.dumps(results, indent=2, sort_keys=True))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SpinQ Tomography")
    parser.add_argument("-m", "--mode", choices=["sim", "qpu", "draw"], default="sim", help="Execution mode: sim (simulator), qpu (real computer), or draw (print circuit)")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f","--full", type=int, choices=[2, 3], help="Number of qubits for full tomography (2 or 3)")
    group.add_argument("-s","--single", type=str, help="Measure a single observable (e.g., XX, XYZ)")
    
    args = parser.parse_args()

    if args.single:
        result = measure_observable(args.single, args.mode)
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        full_qubits = args.full if args.full is not None else 3
        full(args.mode, full_qubits)
