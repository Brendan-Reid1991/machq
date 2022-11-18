import pytest

from machq.codes import RotatedPlanarCodeGadget
from machq.types import Qubit


class TestRotatedPlanarCodeGadget:
    @pytest.mark.parametrize("distance", [3, 5, 7, 9, 11, 13, 15, 17])
    def test_x_flags_are_always_defined_off_correct_aux(self, distance):
        code = RotatedPlanarCodeGadget(x_distance=distance, z_distance=distance)

        assert all(
            flag - aux == Qubit(0.5, 0.5)
            for aux, flag in zip(code.x_auxiliary_qubits, code.x_flags)
        )

    @pytest.mark.parametrize("distance", [3, 5, 7, 9, 11, 13, 15, 17])
    def test_z_flags_are_always_defined_off_correct_aux(self, distance):
        code = RotatedPlanarCodeGadget(x_distance=distance, z_distance=distance)

        assert all(
            flag - aux == Qubit(0.5, 0.5)
            for aux, flag in zip(code.z_auxiliary_qubits, code.z_flags)
        )

    @pytest.mark.parametrize("distance", [3, 5, 7, 9, 11, 13, 15, 17])
    def test_flag_and_aux_ordering_is_correct(self, distance):
        code = RotatedPlanarCodeGadget(x_distance=distance, z_distance=distance)

        assert all(
            flag - aux == Qubit(0.5, 0.5)
            for aux, flag in zip(code.auxiliary_qubits, code.flag_qubits)
        )
