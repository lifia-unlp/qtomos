# lib/reconstruction_strategy.py

from abc import ABC, abstractmethod
import numpy as np

class ReconstructionStrategy(ABC):
    @abstractmethod
    def reconstruct(self, measurements: dict, n_qubits: int, endian: str) -> np.ndarray:
        """Reconstructs the density matrix from the raw measurements."""
        pass
