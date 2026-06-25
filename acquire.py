#acquire.py

import json
import argparse
from lib.acquisition import acquire_tomography_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Acquire SpinQ Tomographic Data")
    parser.add_argument("-m", "--mode", choices=["sim", "qpu", "draw"], default="sim", help="Execution mode: sim (simulator), qpu (real computer), or draw (print circuit)")
    parser.add_argument("-e", "--endian", choices=["big", "little"], default="big", help="Endianness for output bitstrings: big (q[0] is leftmost) or little (q[0] is rightmost)")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots for execution")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f","--full", type=int, choices=[2, 3], help="Number of qubits for full tomography (2 or 3)")
    group.add_argument("-s","--single", type=str, help="Measure a single observable (e.g., XX, XYZ)")
    
    args = parser.parse_args()

    output = acquire_tomography_data(
        mode=args.mode,
        single=args.single,
        full_qubits=args.full,
        endian=args.endian,
        shots=args.shots
    )

    print(json.dumps(output, indent=2, sort_keys=True))
