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
        if isinstance(other, tuple) or isinstance(other, list):
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
        self.idling_qubits = {}

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
            self.idling_qubits[idx] = 0

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
            x
            in [
                line.targets_copy()[0].value
                for line in self.circuit
                if line.name == "QUBIT_COORDS"
            ]
            for x in qubits
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
        self.idling_qubits[ctrl] = 1
        self.idling_qubits[targ] = 1

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
        self.idling_qubits[qubit] = 1

    def time_step(self, idle_noise: Tuple[str, float]):
        """Add a time step here to indicate a gate layer
        terminating. TODO Idle noise will be added to qubits
        that did not participate in any gates since the previous
        time step.
        """
        stim_string, noise_param = idle_noise
        self.circuit.append(
            name=stim_string,
            targets=[
                qubit for qubit, idling in self.idling_qubits.items() if idling == 0
            ],
            arg=noise_param,
        )
        self.circuit.append("TICK")

    def reset_qubits(self, reset_noise: Tuple[str, float], qubits: List[int] = None):
        """Reset qubits into the Z basis.

        Parameters
        ----------
        reset_noise : Tuple[str, float]
            Which noise channel and strength to use.
        qubits : List[int], optional
            Qubits to reset, by default None. If None, all qubits are reset.
        """
        stim_string, noise_param = reset_noise
        qubits = range(self.circuit.num_qubits) if qubits is None else qubits
        self.circuit.append(name=stim_string, targets=qubits, arg=noise_param)

    def measure_qubits(self, measurement_flip: float, qubits: List[int]):
        """Measure qubits in the Z basis.

        Parameters
        ----------
        measurement_flip : float
            Probability of a measurement being recorded incorrectly.
        qubits : List[int]
            List of qubits to measure.
        """
        self.circuit.append("M", targets=qubits, arg=measurement_flip)

    def detectors(
        self,
        lookback_indices: List[int] | List[List[int]],
        arguments: List[Tuple],
    ):
        """Add detectors to the circuit, taking the relevant
        lookback indices and the arguments associated with each.

        Parameters
        ----------
        lookback_indices : List[int] | List[Tuple[int, int]]
            Indices in the measurement history to assign detectors to.
        arguments : List[Tuple]
            Labels to assign to each detector. Must have the same length as
            the lookback indices.
        """
        if len(arguments) != len(lookback_indices):
            raise ValueError("Mismatch between lookback indices and arguments given.")

        for lookbacks, arg in zip(lookback_indices, arguments):
            lookbacks = [lookbacks] if isinstance(lookbacks, int) else lookbacks
            self.circuit.append(
                name="DETECTOR",
                targets=[stim.target_rec(x) for x in lookbacks],
                arg=arg,
            )
