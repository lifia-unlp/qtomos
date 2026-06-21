# lib/mle_least_squares.py

import numpy as np
import scipy.optimize as opt
from lib.reconstruction_strategy import ReconstructionStrategy
from lib.utils import (
    generate_all_pauli_strings,
    matches,
    marginal_expectation_value,
    construct_pauli_string,
)

class MleLeastSquaresStrategy(ReconstructionStrategy):
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
        num_params = dim**2
        
        def params_to_rho(params):
            T = np.zeros((dim, dim), dtype=complex)
            idx = 0
            for i in range(dim):
                T[i, i] = params[idx]
                idx += 1
                for j in range(i):
                    T[i, j] = params[idx] + 1j * params[idx+1]
                    idx += 2
            rho = T @ T.conj().T
            trace = np.trace(rho)
            if trace == 0:
                return rho
            return rho / trace
        
        pauli_matrices = {p_str: construct_pauli_string(p_str) for p_str in exp_vals.keys()}
        
        def cost_func(params):
            rho = params_to_rho(params)
            cost = 0.0
            for p_str, exp_val_measured in exp_vals.items():
                P = pauli_matrices[p_str]
                exp_val_rho = np.real(np.trace(rho @ P))
                cost += (exp_val_rho - exp_val_measured)**2
            return cost
        
        initial_params = np.zeros(num_params)
        idx = 0
        for i in range(dim):
            initial_params[idx] = 1.0
            idx += 1
            for j in range(i):
                idx += 2
                
        result = opt.minimize(cost_func, initial_params, method='L-BFGS-B')
        return params_to_rho(result.x)
