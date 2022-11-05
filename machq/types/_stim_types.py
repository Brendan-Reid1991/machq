from __future__ import annotations
from typing import List, Tuple, Optional, NamedTuple
import stim

from machq.noise import NoiseProfile, NoiseChannels, DepolarizingNoise

ONE_QUBIT_GATES = [
    "H",
    "S",
    "S_DAG",
    "X",
    "SQRT_X",
    "SQRT_X_DAG",
    "Y",
    "SQRT_Y",
    "SQRT_Y_DAG",
    "Z",
]

TWO_QUBIT_GATES = [
    "CX",
]


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

    def __init__(self, noise_profile: NoiseProfile = DepolarizingNoise(p=0)):
        self.circuit = stim.Circuit()

        self.noise_profile = noise_profile
        self.single_qubit_gate_noise = self.noise_profile.single_qubit_gate_noise
        self.two_qubit_gate_noise = self.noise_profile.two_qubit_gate_noise
        self.measurement_flip_prob = self.noise_profile.measurement_flip_prob
        self.reset_noise = self.noise_profile.reset_noise
        self.idle_noise = self.noise_profile.idle_noise

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

    def CX(self, qubits: List[int]):
        """A convenience function that streamlines the use of
        a CNOT gate in stim.

        Parameters
        ----------
        qubits : List[int]
            List of qubits to apply CX gates to.
            Even indexed qubits are controls,
            odd indexed qubits are targets.
        """
        if len(qubits) % 2 != 0:
            raise ValueError("Odd number of qubits passed to a CX gate.")

        self._check_qubits_exist(qubits=qubits)

        self.circuit.append("CX", qubits)
        stim_string, noise_param = self.two_qubit_gate_noise
        self.circuit.append(name=stim_string, targets=qubits, arg=noise_param)

        for qubit in qubits:
            self.idling_qubits[qubit] = 1

    def H(self, qubits: int | List[int]):
        """A convenience function that streamlines the use of
        a Hadamard gate in stim.

        Parameters
        ----------
        qubits : int | List[int]
            Qubit(s) to apply the CNOT to.
        """
        qubits = qubits if isinstance(qubits, List) else [qubits]
        self._check_qubits_exist(qubits=qubits)
        self.circuit.append("H", qubits)
        stim_string, noise_param = self.single_qubit_gate_noise
        self.circuit.append(name=stim_string, targets=qubits, arg=noise_param)

        for qubit in qubits:
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
        for key in self.idling_qubits.keys():
            self.idling_qubits[key] = 0

    def reset_qubits(
        self,
        qubits: List[int] = None,
        reset_channel: Callable = NoiseChannels.XError,
    ):
        """Reset qubits into the Z basis.

        Parameters
        ----------
        qubits : List[int], optional
            Qubits to reset, by default None
        reset_channel : Callable, optional
            Which noise channel to run the reset gate through, by default XError
        """
        stim_string, noise_param = reset_channel(self.reset_noise)
        qubits = range(self.circuit.num_qubits) if qubits is None else qubits
        self.circuit.append(name="R", targets=qubits)
        self.circuit.append(name=stim_string, targets=qubits, arg=noise_param)

    def measure_qubits(self, qubits: List[int]):
        """Measure qubits in the Z basis.

        Parameters
        ----------
        qubits : List[int]
            List of qubits to measure.
        """
        self.circuit.append("M", targets=qubits, arg=self.measurement_flip_prob)

    def detectors(self, lookbacks_and_args: List[Tuple[List, Tuple]]):
        """Add detectors to the circuit, taking the relevant
        lookback indices and the arguments associated with each.

        Parameters
        ----------
        lookbacks_and_args : List[Tuple[List, Tuple]]
            Unpacking this give you the list of lookback arguments
            and the list of relevant arguments.

        Raises
        ------
        ValueError
            If the length of the lookback indices and arguments do not match up.
        """
        lookback_indices = [x[0] for x in lookbacks_and_args]
        arguments = [x[1] for x in lookbacks_and_args]

        if len(arguments) != len(lookback_indices):
            raise ValueError("Mismatch between lookback indices and arguments given.")

        for lookbacks, arg in zip(lookback_indices, arguments):
            lookbacks = [lookbacks] if isinstance(lookbacks, int) else lookbacks
            self.circuit.append(
                name="DETECTOR",
                targets=[stim.target_rec(x) for x in lookbacks],
                arg=arg,
            )

    def add_logical(self, indices: List[int]):
        """Add a logical observable to the circuit.

        Parameters
        ----------
        indices : List[int]
            Measurement record indices to include in the logical
        """
        self.circuit.append(
            "OBSERVABLE_INCLUDE", targets=[stim.target_rec(x) for x in indices], arg=(0)
        )
