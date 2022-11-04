import pytest

from machq.codes import RotatedPlanarCode


class TestRotatedPlanarCode:
    @pytest.mark.fixture(scope="function")
    def rp3x3(self):
        return RotatedPlanarCode(x_distance=3, z_distance=3)

    def test_correct_number_of_qubits_for_3x3(self, rp3x3):
        assert len(rp3x3.qubit_coords) == 17
