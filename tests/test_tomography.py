import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
from lib.utils import (
    matches,
    generate_all_pauli_strings,
    marginal_expectation_value,
)
from lib.linear_inversion import LinearInversionStrategy
from lib.mle_least_squares import MleLeastSquaresStrategy

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

    def test_marginal_expectation_value_endianness(self):
        # 2 qubits. counts: {"01": 100}
        # In big-endian:
        # bit 0 is '0' (qubit 0), bit 1 is '1' (qubit 1)
        # In little-endian (reversed):
        # bit 0 is '0' (qubit 1), bit 1 is '1' (qubit 0)
        counts_big = {"01": 100}
        counts_little = {"10": 100} # reversed
        
        # Test big-endian (where XI extracts qubit 0 -> bit 0 -> '0' -> eigenvalue +1)
        val_xi_big = marginal_expectation_value(counts_big, "XI", "XX")
        self.assertAlmostEqual(val_xi_big, 1.0)
        
        # Test little-endian (when reversed back to big-endian: {"10": 100})
        # XI extracts qubit 0 -> bit 0 -> '1' -> eigenvalue -1
        val_xi_little = marginal_expectation_value(counts_little, "XI", "XX")
        self.assertAlmostEqual(val_xi_little, -1.0)

        # Test IX big-endian (qubit 1 -> bit 1 -> '1' -> eigenvalue -1)
        val_ix_big = marginal_expectation_value(counts_big, "IX", "XX")
        self.assertAlmostEqual(val_ix_big, -1.0)

        # Test IX little-endian (reversed: qubit 1 -> bit 1 -> '0' -> eigenvalue +1)
        val_ix_little = marginal_expectation_value(counts_little, "IX", "XX")
        self.assertAlmostEqual(val_ix_little, 1.0)

class TestReconstructionStrategies(unittest.TestCase):
    def test_reconstruction_end_to_end_big_endian(self):
        measurements = {
            "XX": {"00": 512, "11": 512},
            "XY": {"00": 256, "01": 256, "10": 256, "11": 256},
            "XZ": {"00": 256, "01": 256, "10": 256, "11": 256},
            "YX": {"00": 256, "01": 256, "10": 256, "11": 256},
            "YY": {"01": 512, "10": 512},
            "YZ": {"00": 256, "01": 256, "10": 256, "11": 256},
            "ZX": {"00": 256, "01": 256, "10": 256, "11": 256},
            "ZY": {"00": 256, "01": 256, "10": 256, "11": 256},
            "ZZ": {"00": 512, "11": 512},
        }
        
        for strategy in [LinearInversionStrategy(), MleLeastSquaresStrategy()]:
            rho = strategy.reconstruct(measurements, 2, "big")
            expected_rho = np.array([
                [0.5, 0, 0, 0.5],
                [0,   0, 0, 0],
                [0,   0, 0, 0],
                [0.5, 0, 0, 0.5]
            ])
            np.testing.assert_allclose(rho, expected_rho, atol=0.05)

    def test_reconstruction_end_to_end_little_endian(self):
        # Mock counts for |01> (qubit 0 is 0, qubit 1 is 1) in little-endian.
        measurements = {
            "XX": {"00": 256, "01": 256, "10": 256, "11": 256},
            "XY": {"00": 256, "01": 256, "10": 256, "11": 256},
            "XZ": {"10": 512, "11": 512}, # Z on qubit 1 (bit 0 is always 1).
            "YX": {"00": 256, "01": 256, "10": 256, "11": 256},
            "YY": {"00": 256, "01": 256, "10": 256, "11": 256},
            "YZ": {"10": 512, "11": 512}, # Z on qubit 1 (bit 0 is always 1).
            "ZX": {"00": 512, "10": 512}, # Z on qubit 0 (bit 1 is always 0).
            "ZY": {"00": 512, "10": 512}, # Z on qubit 0 (bit 1 is always 0).
            "ZZ": {"10": 1024},
        }
        
        # In the standard big-endian basis, the state |qubit1=1, qubit0=0> is at index 1 (|01>).
        expected_rho = np.zeros((4, 4))
        expected_rho[1, 1] = 1.0
        
        for strategy in [LinearInversionStrategy(), MleLeastSquaresStrategy()]:
            rho = strategy.reconstruct(measurements, 2, "little")
            np.testing.assert_allclose(rho, expected_rho, atol=0.05)

if __name__ == '__main__':
    unittest.main()
