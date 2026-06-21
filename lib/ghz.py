# lib/ghz.py

import numpy as np
from spinqit import Circuit
from spinqit import H, CX, Sd

class Ghz(Circuit):

    def __init__(self, nqubits: int, name: str = 'ghz'):
            super().__init__(name)
            self.nqubits = nqubits
            self.reg = self.allocateQubits(nqubits)
            self.ghz()

    def ghz(self):
        self << (H, self.reg[0])
        for i in range(1, self.nqubits):
            self.append(CX, [self.reg[0], self.reg[i]])

    def observe_X_and_change_base(self, qubit: int):
        self << (H, self.reg[qubit])

    def observe_Y_and_change_base(self, qubit: int):
        self << (Sd, self.reg[qubit])
        self << (H, self.reg[qubit])

    def observe_Z_and_change_base(self, qubit: int):
        pass

    def prepare_ghz_observation(self, observable: str):
        basis_change = {
            "X": self.observe_X_and_change_base,
            "Y": self.observe_Y_and_change_base,
            "Z": self.observe_Z_and_change_base,
        }
        for qubit_index in range(self.nqubits):
            pauli = observable[qubit_index]
            basis_change[pauli](qubit_index)

    @staticmethod
    def ideal(n_qubits: int) -> np.ndarray:
        """Returns the density matrix of the ideal GHZ state."""
        dim = 2 ** n_qubits
        state = np.zeros(dim, dtype=complex)
        state[0] = 1.0 / np.sqrt(2)
        state[-1] = 1.0 / np.sqrt(2)
        rho = np.outer(state, state.conj())
        return rho
