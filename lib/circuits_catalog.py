# lib/circuits_catalog.py

from spinqit import Circuit
from spinqit import H, CX

def create_ghz(nqubits: int, name: str = 'ghz') -> Circuit:
    """
    Generates a GHZ state preparation circuit for n qubits.
    """
    c = Circuit(name)
    c.allocateQubits(nqubits)
    
    c << (H, 0)
    for i in range(1, nqubits):
        c.append(CX, [0, i])
        
    return c
