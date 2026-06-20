#reconstruct.py

import argparse
import json
import numpy as np
import scipy.optimize as opt

def get_pauli(label):
    """Return the Pauli matrix corresponding to the label."""
    paulis = {
        'I': np.array([[1, 0], [0, 1]], dtype=complex),
        'X': np.array([[0, 1], [1, 0]], dtype=complex),
        'Y': np.array([[0, -1j], [1j, 0]], dtype=complex),
        'Z': np.array([[1, 0], [0, -1]], dtype=complex)
    }
    return paulis[label]

def construct_pauli_string(p_str):
    """Construct an N-qubit Pauli matrix from a string (e.g. 'XX')."""
    result = np.array([[1]])
    for p in p_str:
        result = np.kron(result, get_pauli(p))
    return result

def expectation_value(counts, endian="big"):
    """
    Calculate the expectation value from counts.
    If the bitstring has an even number of 1s, it corresponds to eigenvalue +1.
    If it has an odd number of 1s, it corresponds to eigenvalue -1.
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0
    
    exp_val = 0.0
    for bitstring, count in counts.items():
        # count number of 1s
        ones = bitstring.count('1')
        eigenvalue = 1 if ones % 2 == 0 else -1
        exp_val += eigenvalue * (count / total)
        
    return exp_val

def linear_inversion(exp_vals, n_qubits):
    """Reconstruct density matrix using linear inversion."""
    dim = 2**n_qubits
    rho = np.zeros((dim, dim), dtype=complex)
    
    for p_str, exp_val in exp_vals.items():
        P = construct_pauli_string(p_str)
        rho += exp_val * P
        
    rho = rho / (2**n_qubits)
    return rho

def mle_reconstruction(exp_vals, n_qubits):
    """Reconstruct density matrix using Maximum Likelihood Estimation (MLE)."""
    dim = 2**n_qubits
    # Parameterize T matrix using Cholesky-like factorization to ensure positive semi-definite
    # T is lower triangular. For a complex matrix of dim x dim, we need dim^2 real parameters.
    # The parameters are t_i (real diagonal) and t_{ij} (complex off-diagonal).
    
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
    
    # Initialize with identity-like params
    initial_params = np.zeros(num_params)
    idx = 0
    for i in range(dim):
        initial_params[idx] = 1.0 # diagonal
        idx += 1
        for j in range(i):
            idx += 2 # off-diagonal
            
    result = opt.minimize(cost_func, initial_params, method='L-BFGS-B')
    return params_to_rho(result.x)

def ideal_ghz_state(n_qubits):
    """Returns the density matrix of an ideal N-qubit GHZ state."""
    dim = 2**n_qubits
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0 / np.sqrt(2)
    state[-1] = 1.0 / np.sqrt(2)
    rho = np.outer(state, state.conj())
    return rho

def fidelity(rho1, rho2):
    """Calculate the fidelity between a reconstructed state and an ideal pure state."""
    return np.real(np.trace(rho1 @ rho2))

def plot_density_matrix(rho, title):
    """Plots a 3D cityscape of the real and imaginary parts of the density matrix."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.ticker import MultipleLocator
    except ImportError:
        print("Matplotlib is not installed. Plotting skipped.")
        return

    dim = rho.shape[0]
    
    fig = plt.figure(figsize=(10, 4))
    
    # Real part
    ax1 = fig.add_subplot(121, projection='3d')
    xpos, ypos = np.meshgrid(np.arange(dim), np.arange(dim))
    xpos = xpos.flatten()
    ypos = ypos.flatten()
    zpos = np.zeros(dim*dim)
    dx = np.ones(dim*dim) * 0.8
    dy = np.ones(dim*dim) * 0.8
    dz = np.real(rho).flatten()
    ax1.bar3d(xpos, ypos, zpos, dx, dy, dz, shade=True, color='b', alpha=0.8)
    ax1.set_zlim(-1, 1)
    ax1.set_title("Real Part")
    ax1.xaxis.set_major_locator(MultipleLocator(1))
    ax1.yaxis.set_major_locator(MultipleLocator(1))

    # Imaginary part
    ax2 = fig.add_subplot(122, projection='3d')
    dz_imag = np.imag(rho).flatten()
    ax2.bar3d(xpos, ypos, zpos, dx, dy, dz_imag, shade=True, color='r', alpha=0.8)
    ax2.set_zlim(-1, 1)
    ax2.set_title("Imaginary Part")
    ax2.xaxis.set_major_locator(MultipleLocator(1))
    ax2.yaxis.set_major_locator(MultipleLocator(1))

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="State Reconstruction for SpinQ Tomography")
    parser.add_argument("-f", "--file", type=str, required=True, help="Input JSON file containing measurement counts")
    parser.add_argument("-e", "--endian", choices=["big", "little"], default="big", help="Endianness of the input data")
    parser.add_argument("-m", "--method", choices=["linear", "mle"], default="mle", help="Reconstruction method (linear or mle)")
    parser.add_argument("-p", "--plot", action="store_true", help="Plot the density matrix cityscape")
    args = parser.parse_args()

    with open(args.file, 'r') as f:
        data = json.load(f)

    observables = list(data.keys())
    if not observables:
        print("Error: JSON file is empty or has no observables.")
        return
    
    n_qubits = len(observables[0])
    print(f"Inferred number of qubits: {n_qubits}")

    exp_vals = {}
    for p_str, counts in data.items():
        exp_vals[p_str] = expectation_value(counts, args.endian)

    # Ensure Identity is included
    id_str = 'I' * n_qubits
    exp_vals[id_str] = 1.0

    print(f"Reconstructing density matrix using {args.method.upper()} method...")
    if args.method == "linear":
        rho = linear_inversion(exp_vals, n_qubits)
    else:
        rho = mle_reconstruction(exp_vals, n_qubits)

    rho_ideal = ideal_ghz_state(n_qubits)
    f_val = fidelity(rho, rho_ideal)

    print("\n--- Reconstruction Results ---")
    print(f"Fidelity w.r.t ideal {n_qubits}-qubit GHZ state: {f_val:.4f}")
    
    tr_rho = np.trace(rho)
    print(f"Trace: {tr_rho.real:.4f}")
    
    purity = np.trace(rho @ rho)
    print(f"Purity: {purity.real:.4f}")

    print("\nDensity Matrix (Real part):")
    print(np.round(np.real(rho), 4))
    print("\nDensity Matrix (Imaginary part):")
    print(np.round(np.imag(rho), 4))

    if args.plot:
        plot_density_matrix(rho, f"{n_qubits}-Qubit GHZ Reconstructed State ({args.method.upper()})")

if __name__ == "__main__":
    main()
