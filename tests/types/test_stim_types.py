import pytest
import numpy as np

from machq.types import Circuit, Qubit


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
        circuit_2q.CX(0, 1)
        assert circuit_2q.as_stim[-1].name == "CX" and [
            x.value for x in circuit_2q.as_stim[-1].targets_copy()
        ] == [0, 1]

    def test_H(self, circuit_1q):
        circuit_1q.H(0)
        assert circuit_1q.as_stim[-1].name == "H" and [
            x.value for x in circuit_1q.as_stim[-1].targets_copy()
        ] == [0]

    def test_check_qubits_exist_raises_error(self, circuit_1q):
        with pytest.raises(ValueError, match=r".*Not all qubit(s)*"):
            circuit_1q.H(100)


class TestQubit:
    @pytest.mark.parametrize(
        "q1, q2, qsum",
        [
            (Qubit(0, 0), Qubit(1, 2), Qubit(1, 2)),
            (Qubit(10, 12), Qubit(4, 3), Qubit(14, 15)),
            (Qubit(54, 1), Qubit(44, 10002), Qubit(98, 10003)),
        ],
    )
    def test_addition_of_qubits(self, q1, q2, qsum):
        assert q1 + q2 == qsum

    @pytest.mark.parametrize(
        "q1, q2, qsum",
        [
            (Qubit(0, 0), (1, 2), Qubit(1, 2)),
            (Qubit(10, 12), (4, 3), Qubit(14, 15)),
            (Qubit(54, 1), (44, 10002), Qubit(98, 10003)),
        ],
    )
    def test_addition_of_qubits_with_tuples(self, q1, q2, qsum):
        assert q1 + q2 == qsum

    @pytest.mark.parametrize(
        "q1, q2, qsum",
        [
            (Qubit(0, 0), [1, 2], Qubit(1, 2)),
            (Qubit(10, 12), [4, 3], Qubit(14, 15)),
            (Qubit(54, 1), [44, 10002], Qubit(98, 10003)),
        ],
    )
    def test_addition_of_qubits_with_lists(self, q1, q2, qsum):
        assert q1 + q2 == qsum

    @pytest.mark.parametrize(
        "q1, x, qmul",
        [
            (Qubit(0, 0), 22, Qubit(0, 0)),
            (Qubit(10, 12), 1, Qubit(10, 12)),
            (Qubit(54, 1), 4, Qubit(216, 4)),
        ],
    )
    def test_multiplication_of_qubits(self, q1, x, qmul):
        assert q1 * x == qmul

    @pytest.mark.parametrize(
        "func, entry1, entry2",
        [
            ("add", Qubit(0, 0), {0: 1, 1: 0}),
            ("multiply", Qubit(10, 12), 0.1),
        ],
    )
    def test_not_implemented_errors_are_raised(self, func, entry1, entry2):
        with pytest.raises(NotImplementedError):
            if func == "add":
                entry1 + entry2
            if func == "multiply":
                entry1 * entry2

    def test_eq_is_false_when_not_equal(self):
        assert not Qubit(1, 0) == Qubit(0, 1)
