import pytest
import stim

from machq.decoders import PyMatching
from machq.types import Circuit


class TestPyMatching:
    @pytest.fixture(scope="class")
    def circuit3x3(self):
        return Circuit.from_stim(
            stim_circuit=stim.Circuit.generated(
                "surface_code:rotated_memory_z",
                rounds=3,
                distance=3,
                after_clifford_depolarization=0.001,
                after_reset_flip_probability=0.001,
                before_measure_flip_probability=0.001,
                before_round_data_depolarization=0.001,
            )
        )

    def test_str_output(self, circuit3x3):
        assert str(PyMatching(circuit=circuit3x3)) == "PyMatching"

    def test_logical_fail_probability(self, circuit3x3):
        assert (
            0
            <= PyMatching(circuit=circuit3x3).logical_failure_probability(num_shots=1e4)
            <= 1
        )
