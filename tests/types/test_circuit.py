import pytest
import numpy as np

from machq.types import Circuit


class TestCircuit:
    @pytest.fixture(scope="function")
    def empty_circuit(self):
        return Circuit()

    @pytest.fixture(scope="function")
    def circuit_1q(self):
        circ = Circuit()
        circ.add_qubits()
        return circ

    @pytest.fixture(scope="function")
    def circuit_2q(self):
        circ = Circuit()
        circ.add_qubits(2)
        return circ

    @pytest.mark.parametrize("repeats", [50])
    def test_add_qubits_with_indices(self, empty_circuit, repeats):
        for _ in range(repeats):
            empty_circuit.clear
            num_qubits = np.random.randint(0, 1000)
            empty_circuit.add_qubits(num_qubits)
            assert (
                len(empty_circuit.as_stim) == num_qubits
                and all(line.name == "QUBIT_COORDS" for line in empty_circuit.as_stim)
                and all(
                    line.gate_args_copy() == [idx]
                    for idx, line in enumerate(empty_circuit.as_stim)
                )
            )

    @pytest.mark.parametrize(
        "coords",
        [
            ([(0, 0), (0, 1), (1, 0)]),
            ([(x, y) for x in range(10) for y in range(10)]),
            ([(10, 11)]),
        ],
    )
    def test_add_qubits_with_coords(self, empty_circuit, coords):
        num_qubits = len(coords)
        empty_circuit.add_qubits(num_qubits, coords)
        assert (
            len(empty_circuit.as_stim) == num_qubits
            and all(line.name == "QUBIT_COORDS" for line in empty_circuit.as_stim)
            and [line.gate_args_copy() for line in empty_circuit.as_stim]
            == list(map(list, coords))
        )

    def test_CX(self, circuit_2q):
        circuit_2q.CX([0, 1])
        assert circuit_2q.as_stim[-1].name == "DEPOLARIZE2" and [
            x.value for x in circuit_2q.as_stim[-1].targets_copy()
        ] == [0, 1]

        assert circuit_2q.as_stim[-2].name == "CX" and [
            x.value for x in circuit_2q.as_stim[-2].targets_copy()
        ] == [0, 1]

    def test_H(self, circuit_1q):
        circuit_1q.H(0)
        assert circuit_1q.as_stim[-1].name == "DEPOLARIZE1" and [
            x.value for x in circuit_1q.as_stim[-1].targets_copy()
        ] == [0]
        assert circuit_1q.as_stim[-2].name == "H" and [
            x.value for x in circuit_1q.as_stim[-2].targets_copy()
        ] == [0]

    def test_check_qubits_exist_raises_error(self, circuit_1q):
        with pytest.raises(ValueError, match=r".*Not all qubit(s)*"):
            circuit_1q.H(100)
