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

    @pytest.mark.parametrize("distance", [x for x in range(3, 21, 2)])
    def test_auxiliary_qubit_coords_are_ordered_x_then_z(self, distance):
        code = RotatedPlanarCode(x_distance=distance, z_distance=distance)
        x_len = len(code.x_auxiliary_qubits)
        z_len = len(code.z_auxiliary_qubits)
        assert (
            code.auxiliary_qubits[0:x_len] == code.x_auxiliary_qubits
            and code.auxiliary_qubits[x_len : x_len + z_len] == code.z_auxiliary_qubits
        )

    @pytest.mark.parametrize("distance", [x for x in range(3, 21, 2)])
    def test_qubit_coords_added_to_circuit(self, distance):
        code = RotatedPlanarCode(x_distance=distance, z_distance=distance)

        assert len(code.circuit.as_stim) == len(code.qubit_coords) and all(
            line.name == "QUBIT_COORDS" for line in code.circuit
        )

    @pytest.mark.parametrize("distance", [x for x in range(3, 21, 2)])
    def test_neighbouring_qubits_are_all_data_qubits(self, distance):
        code = RotatedPlanarCode(x_distance=distance, z_distance=distance)

        assert all(
            qubit in code.data_qubits
            for qubit in code._neighbouring_data_qubits(auxiliary_qubit)
            for auxiliary_qubit in code.auxiliary_qubits
        )

    @pytest.mark.parametrize("distance", [x for x in range(3, 21, 2)])
    def test_four_CX_in_measure_syndrome(self, distance):
        code = RotatedPlanarCode(x_distance=distance, z_distance=distance)
        code._measure_syndromes_()
        assert len([line for line in code.circuit if line.name == "CX"]) == 4

    @pytest.mark.parametrize("distance", [x for x in range(3, 21, 2)])
    def test_measurement_and_reset_are_in_circuit(self, distance):
        code = RotatedPlanarCode(x_distance=distance, z_distance=distance)
        code._measure_syndromes_()

        assert all(gate in code.circuit for gate in ["M", "R"])

        measurement_line_index = [
            idx for idx, line in enumerate(code.circuit) if line.name == "M"
        ]
        reset_line_index = [
            idx for idx, line in enumerate(code.circuit) if line.name == "R"
        ]
        assert measurement_line_index < reset_line_index

    @pytest.mark.parametrize("distance", [x for x in range(3, 21, 2)])
    def test_encode_logical_zero(self, distance):
        code = RotatedPlanarCode(x_distance=distance, z_distance=distance)
        code.encode_logical_zero()
        assert (
            all(
                line.name == "DETECTOR"
                for line in code.circuit[-len(code.z_auxiliary_qubits) : :]
            )
            and not code.circuit[-len(code.z_auxiliary_qubits) - 1].name == "DETECTOR"
        )

    @pytest.mark.parametrize("distance", [x for x in range(3, 21, 2)])
    def test_encode_logical_plus(self, distance):
        code = RotatedPlanarCode(x_distance=distance, z_distance=distance)
        code.encode_logical_plus()
        assert (
            all(
                line.name == "DETECTOR"
                for line in code.circuit[-len(code.x_auxiliary_qubits) : :]
            )
            and not code.circuit[-len(code.x_auxiliary_qubits) - 1].name == "DETECTOR"
        )
