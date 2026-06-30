import json
import argparse
import inspect
from dotenv import load_dotenv
from . import circuits_catalog
from .acquisition import measure_observable, measure_all_observables

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Acquire SpinQ Tomographic Data")
    
    # Dynamically discover circuits in the catalog
    circuit_funcs = {
        name.replace("create_", ""): func 
        for name, func in inspect.getmembers(circuits_catalog, inspect.isfunction) 
        if name.startswith("create_")
    }

    parser.add_argument("-m", "--mode", choices=["sim", "qpu", "draw"], required=True, help="Execution mode: sim (simulator), qpu (real computer), or draw (print circuit)")
    parser.add_argument("-c", "--circuit", choices=list(circuit_funcs.keys()), required=True, help="Circuit to prepare")
    parser.add_argument("-q", "--qubits", type=int, help="Number of qubits (inferred from observable if omitted, defaults to 3)")
    parser.add_argument("-s", "--shots", type=int, default=1024, help="Number of shots for execution")
    
    parser.add_argument("-f", "--file", type=str, required=True, help="Output JSON file path")
    parser.add_argument("-o", "--observable", type=str, help="Measure a single observable (e.g., XX, XYZ)")
    
    args = parser.parse_args()

    # Determine number of qubits
    if args.qubits is not None:
        num_qubits = args.qubits
    else:
        num_qubits = len(args.observable) if args.observable else 3
        
    # Retrieve the dynamically selected circuit creation function
    create_func = circuit_funcs[args.circuit]
    c = create_func(num_qubits)
    
    # Check for inconsistencies
    if args.observable and len(args.observable) != c.qubits_num:
        parser.error(f"Length of observable '{args.observable}' ({len(args.observable)}) does not match the actual circuit size ({c.qubits_num} qubits).")

    qpu_config = None
    if args.mode == "qpu":
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
        qpu_config = {
            "ip": ip,
            "port": port,
            "username": username,
            "password": password
        }

    if args.observable:
        output = measure_observable(
            circuit=c,
            observable=args.observable,
            mode=args.mode,
            shots=args.shots,
            qpu_config=qpu_config
        )
    else:
        output = measure_all_observables(
            circuit=c,
            mode=args.mode,
            shots=args.shots,
            qpu_config=qpu_config
        )

    with open(args.file, "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
