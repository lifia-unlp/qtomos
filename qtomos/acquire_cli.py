import json
import argparse
import inspect
from dotenv import load_dotenv
from . import circuits_catalog
from .acquisition import measure_observable, measure_all_observables

def discover_circuits() -> dict:
    """
    Scans the circuits_catalog module to find available circuit builder functions.
    It looks for functions starting with 'create_' and returns a dictionary mapping
    the clean circuit name (without the 'create_' prefix) to the actual function.
    
    Returns:
        dict: A mapping of circuit names (str) to their corresponding builder functions.
    """
    return {
        name.replace("create_", ""): func 
        for name, func in inspect.getmembers(circuits_catalog, inspect.isfunction) 
        if name.startswith("create_")
    }

def build_circuit(circuit_name: str, circuit_funcs: dict, explicit_qubits: int = None, observable: str = None):
    """
    Instantiates a circuit by retrieving its builder function from the discovered catalog.
    
    If the number of qubits is not explicitly provided, it attempts to infer it from 
    the length of the provided observable. If no observable is provided, it defaults to 3 qubits.
    
    Args:
        circuit_name (str): The name of the circuit to build (must be a key in circuit_funcs).
        circuit_funcs (dict): The dictionary of available circuit builder functions.
        explicit_qubits (int, optional): Explicit number of qubits requested.
        observable (str, optional): The observable string to infer qubits from if not explicit.
        
    Returns:
        Circuit: The instantiated SpinQ circuit.
    """
    if explicit_qubits is not None:
        num_qubits = explicit_qubits
    else:
        num_qubits = len(observable) if observable else 3
        
    create_func = circuit_funcs[circuit_name]
    return create_func(num_qubits)

def autogenerate_output_filename(circuit_name: str, qubits_num: int, mode: str) -> str:
    """
    Generates an output filename by finding the next available run number.
    Format: [circuit_name]-[qubits]-[mode]-run_[N].json
    """
    import os
    run_number = 1
    while True:
        filename = f"{circuit_name}-{qubits_num}-{mode}-run_{run_number}.json"
        if not os.path.exists(filename):
            return filename
        run_number += 1


def build_argument_parser(circuit_funcs: dict) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Acquire SpinQ Tomographic Data")
    parser.add_argument("-m", "--mode", choices=["sim", "qpu", "draw"], required=True, help="Execution mode: sim (simulator), qpu (real computer), or draw (print circuit)")
    parser.add_argument("-c", "--circuit", choices=list(circuit_funcs.keys()), required=True, help="Circuit to prepare")
    parser.add_argument("-q", "--qubits", type=int, help="Number of qubits (inferred from observable if omitted, defaults to 3)")
    parser.add_argument("-s", "--shots", type=int, default=1024, help="Number of shots for execution")
    parser.add_argument("-f", "--file", type=str, help="Output JSON file path")
    parser.add_argument("-o", "--observable", type=str, help="Measure a single observable (e.g., XX, XYZ)")
    return parser

def validate_observables_length(circuit, observable_arg: str, parser: argparse.ArgumentParser):
    if observable_arg and len(observable_arg) != circuit.qubits_num:
        parser.error(f"Length of observable '{observable_arg}' ({len(observable_arg)}) does not match the actual circuit size ({circuit.qubits_num} qubits).")

def load_qpu_config_from_env(parser: argparse.ArgumentParser) -> dict:
    import os
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
        parser.error(f"Missing required environment variables for QPU connection: {', '.join(missing)}")
        
    try:
        port = int(port_str)
    except ValueError:
        parser.error(f"QTOMOS_PORT must be an integer, but got: '{port_str}'")

    print(f"Using QPU configuration: IP={ip}, PORT={port}, USERNAME={username}, PASSWORD={password}")
    return {
        "ip": ip,
        "port": port,
        "username": username,
        "password": password
    }

def execute_measurement(circuit, args: argparse.Namespace, qpu_config: dict) -> dict:
    if args.observable:
        return measure_observable(
            circuit=circuit,
            observable=args.observable,
            mode=args.mode,
            shots=args.shots,
            qpu_config=qpu_config
        )
    else:
        return measure_all_observables(
            circuit=circuit,
            mode=args.mode,
            shots=args.shots,
            qpu_config=qpu_config
        )

def main():
    load_dotenv()
    
    circuit_funcs = discover_circuits()
    parser = build_argument_parser(circuit_funcs)
    args = parser.parse_args()

    c = build_circuit(args.circuit, circuit_funcs, args.qubits, args.observable)
    
    if not args.file:
        args.file = autogenerate_output_filename(args.circuit, c.qubits_num, args.mode)
        print(f"Output file not specified. Using auto-generated filename: {args.file}")
    
    validate_observables_length(c, args.observable, parser)

    qpu_config = None
    if args.mode == "qpu":
        qpu_config = load_qpu_config_from_env(parser)

    output = execute_measurement(c, args, qpu_config)

    with open(args.file, "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
