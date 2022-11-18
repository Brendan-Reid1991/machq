import pytest
import numpy as np

from machq.types import Qubit


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
        "q1, q2, qsub",
        [
            (Qubit(1, 2), Qubit(0, 0), Qubit(1, 2)),
            (Qubit(4, 3), Qubit(10, 12), Qubit(-6, -9)),
            (Qubit(44, 10002), Qubit(54, 1), Qubit(-10, 10001)),
        ],
    )
    def test_subtraction_of_qubits(self, q1, q2, qsub):
        assert q1 - q2 == qsub

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
