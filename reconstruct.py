#reconstruct.py

import argparse
import json
import numpy as np

from lib.linear_inversion import LinearInversionStrategy
from lib.mle_least_squares import MleLeastSquaresStrategy

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
    parser.add_argument("-m", "--method", choices=["linear", "mle"], default="mle", help="Reconstruction method (linear or mle)")
    parser.add_argument("-p", "--plot", action="store_true", help="Plot the density matrix cityscape")
    args = parser.parse_args()

    with open(args.file, 'r') as f:
        data = json.load(f)

    metadata = data["metadata"]
    measurements = data["measurements"]
    n_qubits = metadata["qubits"]
    endian = metadata["endian"]

    observables = list(measurements.keys())
    if not observables:
        print("Error: JSON file is empty or has no observables.")
        return
    
    print(f"Inferred number of qubits: {n_qubits}")

    strategies = {
        "linear": LinearInversionStrategy(),
        "mle": MleLeastSquaresStrategy()
    }
    
    strategy = strategies[args.method]
    print(f"Reconstructing density matrix using {args.method.upper()} method...")
    rho = strategy.reconstruct(measurements, n_qubits, endian)

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
