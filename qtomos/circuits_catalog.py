# lib/circuits_catalog.py

from spinqit import Circuit, H, CX, Ry, Rx, X
import math
import random

def create_ghz(qubits: int) -> Circuit:
    """Generates a GHZ state preparation circuit."""
    c = Circuit()
    c.name = "ghz"
    c.allocateQubits(qubits)
    
    c << (H, 0)
    for i in range(1, qubits):
        c.append(CX, [0, i])
        
    return c

def create_phi_plus(qubits: int) -> Circuit:
    """Creates a 2-qubit Phi+ Bell state. Ignores qubits > 2."""
    c = Circuit()
    c.name = "phi_plus"
    c.allocateQubits(2)
    c << (H, 0)
    c << (CX, [0, 1])
    return c

def create_w(qubits: int) -> Circuit:
    """Creates a 3-qubit W state. Ignores qubits parameter."""
    c = Circuit()
    c.name = "w"
    c.allocateQubits(3)
    
    # 1. Ry to create 1/sqrt(3)|0> + sqrt(2/3)|1> on q0
    theta = 2 * math.acos(1 / math.sqrt(3))
    c.append(Ry, [0], [], theta)
    
    # 2. Controlled-H equivalent (acts as H on |0> when controlled)
    c.append(Ry, [1], [], math.pi/4)
    c.append(CX, [0, 1])
    c.append(Ry, [1], [], -math.pi/4)
    
    # 3. Entangle q2
    c.append(CX, [1, 2])
    
    # 4. Flip remaining states
    c.append(CX, [0, 1])
    c.append(X, [0])
    
    return c

def create_random(qubits: int) -> Circuit:
    """Creates a random parameterized circuit for the given number of qubits."""
    c = Circuit()
    c.name = "random"
    c.allocateQubits(qubits)
    
    # Apply random rotations
    for i in range(qubits):
        c.append(Rx, [i], [], random.uniform(0, 2*math.pi))
        c.append(Ry, [i], [], random.uniform(0, 2*math.pi))
        
    # Apply entangling chain
    for i in range(qubits - 1):
        c.append(CX, [i, i+1])
        
    return c
