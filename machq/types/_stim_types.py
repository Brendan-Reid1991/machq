from __future__ import annotations
from typing import List, Tuple, Optional, NamedTuple
import stim


class Qubit(NamedTuple):
    """A class that allows easy reference to
    qubit coordinates.
    """

    x: int
    y: int

    def __add__(self, other):
        if isinstance(other, tuple):
            other = Qubit(*other)
        if isinstance(other, Qubit):
            return Qubit(self.x + other.x, self.y + other.y)
        raise NotImplementedError()

    def __mul__(self, other):
        if isinstance(other, int):
            return Qubit(self.x * other, self.y * other)
        raise NotImplementedError()

    def __eq__(self, other):
        if isinstance(other, Qubit):
            return self.x == other.x and self.y == other.y


class Circuit:
    """A class that allows manipulation and
    use of a stim.Circuit() class.
    """

    def __init__(self):
        self.circuit = stim.Circuit()

    def __repr__(self):
        return self.circuit.__repr__()

    def __str__(self):
        return self.circuit.__str__()

    @property
    def as_stim(self):
        return self.circuit

    @property
    def clear(self):
        self.circuit.clear()

    def add_qubits(
        self,
        num_qubits: int = 1,
        qubit_coords: Optional[List[Qubit]] = None,
    ):
        """A function to add qubit identifiers to the stim.Circuit()

        Parameters
        ----------
        num_qubits : int
            How many qubits to add, must be a positive integer.
        qubit_coords : Optional[List[Tuple[float, float]]]
            Optional. Gives qubits coordinate labels; must be supplied
            the order desired, i.e. qubit_coords[idx] is the coordinate
            of qubit # idx.
            # TODO Make this more general
        """
        qubit_coords = qubit_coords if qubit_coords is not None else range(num_qubits)
        for idx, qcoord in enumerate(qubit_coords):
            self.circuit.append("QUBIT_COORDS", idx, qcoord)

    def _check_qubits_exist(self, qubits: List[int] | int):
        """Private function to ensure functions
        are being applied to qubits actually present in
        the circuit.

        Parameters
        ----------
        qubits : List[int] | int
            Qubits to check.
        """
        qubits = qubits if isinstance(qubits, List) else [qubits]

        if not all(
            x in [line.targets_copy()[0].value for line in self.circuit] for x in qubits
        ):
            raise ValueError(f"Not all qubit(s) {qubits} are present in the circuit.")

    def CX(self, ctrl: int, targ: int):
        """A convenience function that streamlines the use of
        a CNOT gate in stim.

        Parameters
        ----------
        ctrl : int
            The index of the control qubit.
        targ : int
            The index of the target qubit.
        """
        self._check_qubits_exist(qubits=[ctrl, targ])

        self.circuit.append("CX", [ctrl, targ])

    def H(self, qubit: int):
        """A convenience function that streamlines the use of
        a Hadamard gate in stim.

        Parameters
        ----------
        qubit : int | Tuple
            Qubit to apply the CNOT to.
        """
        self._check_qubits_exist(qubits=qubit)
        self.circuit.append("H", [qubit])
