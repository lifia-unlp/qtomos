# lib/linear_inversion.py

import numpy as np
from lib.reconstruction_strategy import ReconstructionStrategy
from lib.utils import (
    generate_all_pauli_strings,
    matches,
    marginal_expectation_value,
    construct_pauli_string,
)

class LinearInversionStrategy(ReconstructionStrategy):
    def reconstruct(self, measurements: dict, n_qubits: int, endian: str) -> np.ndarray:
        if endian == "little":
            measurements = {
                obs: {bitstring[::-1]: count for bitstring, count in counts.items()}
                for obs, counts in measurements.items()
            }
            endian = "big"

        all_paulis = generate_all_pauli_strings(n_qubits)
        exp_vals = {}
        for p_str in all_paulis:
            matching_measurements = [m_str for m_str in measurements.keys() if matches(p_str, m_str)]
            if not matching_measurements:
                exp_vals[p_str] = 0.0
                continue
            
            vals = []
            for m_str in matching_measurements:
                val = marginal_expectation_value(measurements[m_str], p_str, m_str)
                vals.append(val)
            exp_vals[p_str] = sum(vals) / len(vals)

        dim = 2**n_qubits
        rho = np.zeros((dim, dim), dtype=complex)
        for p_str, exp_val in exp_vals.items():
            P = construct_pauli_string(p_str)
            rho += exp_val * P
        return rho / dim
