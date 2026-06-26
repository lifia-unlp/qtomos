import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
from qtomos.utils import (
    matches,
    generate_all_pauli_strings,
    marginal_expectation_value,
)
from qtomos.acquisition import measure_observable, measure_all_observables
from qtomos.circuits_catalog import create_phi_plus

class TestTomographyUtils(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(matches("XI", "XX"))
        self.assertTrue(matches("IX", "XX"))
        self.assertTrue(matches("II", "XX"))
        self.assertFalse(matches("XI", "YX"))
        self.assertTrue(matches("XYZ", "XYZ"))
        self.assertFalse(matches("XYZ", "XYX"))

    def test_generate_all_pauli_strings(self):
        paulis_2 = generate_all_pauli_strings(2)
        self.assertEqual(len(paulis_2), 16)
        self.assertIn("II", paulis_2)
        self.assertIn("ZZ", paulis_2)
        self.assertIn("XI", paulis_2)
        
        paulis_3 = generate_all_pauli_strings(3)
        self.assertEqual(len(paulis_3), 64)

    def test_marginal_expectation_value_indexing(self):
        # 2 qubits. counts: {"01": 100}
        # In standard (big-endian) ordering:
        # bit 0 (leftmost) is '0' (qubit 0), bit 1 (rightmost) is '1' (qubit 1)
        counts = {"01": 100}
        
        # Test XI extracts qubit 0 (bit 0 -> '0' -> eigenvalue +1)
        val_xi = marginal_expectation_value(counts, "XI", "XX")
        self.assertAlmostEqual(val_xi, 1.0)
        
        # Test IX extracts qubit 1 (bit 1 -> '1' -> eigenvalue -1)
        val_ix = marginal_expectation_value(counts, "IX", "XX")
        self.assertAlmostEqual(val_ix, -1.0)


class TestAcquisition(unittest.TestCase):
    def test_measure_observable_bell_state(self):
        circuit = create_phi_plus(2)
        
        # Test ZZ measurement (should only contain '00' and '11')
        res_zz = measure_observable(circuit, "ZZ", mode="sim", shots=100)
        counts_zz = res_zz["ZZ"]["counts"]
        self.assertEqual(sum(counts_zz.values()), 100)
        self.assertTrue(set(counts_zz.keys()).issubset({"00", "11"}))
        
        # Test YY measurement (should only contain '01' and '10')
        res_yy = measure_observable(circuit, "YY", mode="sim", shots=100)
        counts_yy = res_yy["YY"]["counts"]
        self.assertEqual(sum(counts_yy.values()), 100)
        self.assertTrue(set(counts_yy.keys()).issubset({"01", "10"}))

    def test_measure_all_observables_bell_state(self):
        circuit = create_phi_plus(2)
        results = measure_all_observables(circuit, mode="sim", shots=50)
        
        self.assertEqual(results["metadata"]["qubits"], 2)
        self.assertEqual(results["metadata"]["endian"], "big")
        self.assertEqual(results["metadata"]["shots"], 50)
        
        measurements = results["measurements"]
        self.assertEqual(len(measurements), 9) # 9 2-qubit Pauli observables
        for obs in ["XX", "XY", "XZ", "YX", "YY", "YZ", "ZX", "ZY", "ZZ"]:
            self.assertIn(obs, measurements)
            self.assertEqual(sum(measurements[obs]["counts"].values()), 50)


if __name__ == '__main__':
    unittest.main()
