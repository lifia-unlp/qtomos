# lib/utils.py

import numpy as np

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

def expectation_value(counts):
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

def marginal_expectation_value(counts, p_str, m_str):
    """
    Calculate the expectation value of a Pauli string p_str (which may contain 'I')
    from the counts of a measured Pauli string m_str (which has no 'I' and matches
    p_str on all non-'I' positions).
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0
    
    active_indices = [i for i, char in enumerate(p_str) if char != 'I']
    if not active_indices:
        return 1.0
        
    exp_val = 0.0
    for bitstring, count in counts.items():
        sub_bits = [bitstring[i] for i in active_indices]
        ones = sub_bits.count('1')
        eigenvalue = 1 if ones % 2 == 0 else -1
        exp_val += eigenvalue * (count / total)
        
    return exp_val

def matches(p_str, m_str):
    """Check if the measured Pauli string m_str matches the target p_str."""
    for p_char, m_char in zip(p_str, m_str):
        if p_char != 'I' and p_char != m_char:
            return False
    return True

def generate_all_pauli_strings(n_qubits):
    import itertools
    return [''.join(p) for p in itertools.product(['I', 'X', 'Y', 'Z'], repeat=n_qubits)]
