# lib/acquisition.py

import copy
import datetime
import os
from dotenv import load_dotenv

from spinqit import NMRConfig, get_basic_simulator, get_compiler, BasicSimulatorConfig, get_nmr, draw as sq_draw, Circuit
from spinqit import H, Sd, QasmBackend
from spinqit.backend.nmr_backend import NMRBackend

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

def append_observation_basis(circuit: Circuit, observable: str):
    """
    Appends the necessary gates to change the measurement basis 
    to match the Pauli observable.
    
    This function applies the required gates (H for X, Sd+H for Y) sequentially 
    to the first N qubits of the circuit, where N is the length of the observable string.
    
    Examples of `observable` strings: "XX", "XY", "XYZ", "ZZZ"
    """
    for qubit_index, pauli in enumerate(observable):
        if pauli == "X":
            circuit << (H, qubit_index)
        elif pauli == "Y":
            circuit << (Sd, qubit_index)
            circuit << (H, qubit_index)
        elif pauli == "Z":
            pass

def simulate(c: Circuit, shots: int = 1024):
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

def run(c: Circuit, shots: int = 1024):
    ip = os.environ.get("QTOMOS_IP")
    port_str = os.environ.get("QTOMOS_PORT")
    username = os.environ.get("QTOMOS_USERNAME")        
    password = os.environ.get("QTOMOS_PASSWORD")
    
    missing = []
    if not ip: missing.append("QTOMOS_IP")
    if not port_str: missing.append("QTOMOS_PORT")
    if not username: missing.append("QTOMOS_USERNAME")
    if not password: missing.append("QTOMOS_PASSWORD")
    
    if missing:
        raise ValueError(f"Missing required environment variables for QPU connection: {', '.join(missing)}")
        
    try:
        port = int(port_str)
    except ValueError:
        raise ValueError(f"QTOMOS_PORT must be an integer, but got: '{port_str}'")
        
    comp = get_compiler("native")
    optimization_level = 0
    exe = comp.compile(c, optimization_level)   
    engine = get_nmr()
    config = NMRConfig()
    config.configure_ip(ip)
    config.configure_port(port)
    config.configure_account(username, password)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    task_name = getattr(c, 'name', "circuit")
    task_desc = f"Execution of {task_name} at {timestamp}"
    config.configure_task(task_name, task_desc)
    config.configure_shots(shots) 
    resultado = engine.execute(exe, config)
    return resultado.counts

def draw(c: Circuit):
    compiler = get_compiler('native')
    ir = compiler.compile(c, level=0)
    name = getattr(c, 'name', "circuit")
    filename = f"{name.replace(' ', '_')}.png"
    sq_draw(ir, filename=filename)
    print(f"Circuit drawing saved to {filename}")

def normalize_counts(counts):
    return {
        str(bitstring): int(count)
        for bitstring, count in counts.items()
    }

def measure_observable(circuit: Circuit, observable: str, mode: str, shots: int = 1024):
    circuit_name = getattr(circuit, 'name', 'circuit')
    print(f"Starting measurement task for circuit '{circuit_name}', observable '{observable}'...")
    
    c = copy.deepcopy(circuit)
    append_observation_basis(c, observable)

    start_time = datetime.datetime.now().astimezone().isoformat()
    
    # Compile to get QASM representations
    compiler = get_compiler('native')
    ir = compiler.compile(c, level=0)
    qasm_str = QasmBackend.convert_ir_to_qasm(ir)
    
    # Assemble to Native hardware IR and get Native QASM
    ir_native = copy.deepcopy(ir)
    try:
        NMRBackend().assemble(ir_native)
        native_qasm_str = QasmBackend.convert_ir_to_qasm(ir_native)
    except Exception as e:
        native_qasm_str = f"Error generating native QASM: {e}"

    if mode == "draw":
        draw(c)
        counts = {}
    elif mode == "qpu":
        counts = run(c, shots)
    else:
        counts = simulate(c, shots)
        
    end_time = datetime.datetime.now().astimezone().isoformat()
    
    print(f"Finished measurement task for circuit '{circuit_name}', observable '{observable}'.")
    
    return {
        observable: {
            "circuit_name": circuit_name,
            "mode": mode,
            "shots": shots,
            "endian": "big",
            "timestamps": {
                "start": start_time,
                "end": end_time
            },
            "counts": normalize_counts(counts),
            "qasm": qasm_str,
            "native": native_qasm_str
        }
    }

def measure_all_observables(circuit: Circuit, mode: str, shots: int = 1024):
    start_time = datetime.datetime.now().astimezone().isoformat()
    results = {}
    qubits = circuit.qubits_num
    observables = TWO_QUBIT_OBSERVABLES if qubits == 2 else THREE_QUBIT_OBSERVABLES
    
    for observable in observables:
        obs_data = measure_observable(circuit, observable, mode, shots)
        res = obs_data[observable]
        
        # Remove common metadata properties to avoid duplication
        res.pop("circuit_name", None)
        res.pop("mode", None)
        res.pop("shots", None)
        res.pop("endian", None)
        
        results[observable] = res

    end_time = datetime.datetime.now().astimezone().isoformat()
    
    return {
        "metadata": {
            "circuit_name": getattr(circuit, 'name', "circuit"),
            "qubits": qubits,
            "mode": mode,
            "shots": shots,
            "endian": "big",
            "timestamps": {
                "start": start_time,
                "end": end_time
            }
        },
        "measurements": results
    }


