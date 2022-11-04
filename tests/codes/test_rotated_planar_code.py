import pytest

from machq.codes import RotatedPlanarCode


class TestRotatedPlanarCode:
    @pytest.fixture(scope="function")
    def rp3x3(self):
        return RotatedPlanarCode(x_distance=3, z_distance=3)

    def test_correct_number_of_qubits_for_3x3(self, rp3x3):
        assert len(rp3x3.qubit_coords) == 17

    @pytest.mark.parametrize(
        "x_distance, z_distance", [(3, 4), (4, 5), (10, 12), (21, 5)]
    )
    def test_rotated_planar_name(self, x_distance, z_distance):
        assert (
            str(RotatedPlanarCode(x_distance=x_distance, z_distance=z_distance))
            == f"rotated_planar_{x_distance}x{z_distance}"
        )

    @pytest.mark.parametrize("distance", [x for x in range(3, 21, 2)])
    def test_qubit_coords_are_unique(self, distance):
        code = RotatedPlanarCode(x_distance=distance, z_distance=distance)
        assert len(set(code.qubit_coords)) == len(code.qubit_coords)
