from __future__ import annotations
from typing import List, Tuple, Optional
import stim

from machq.noise import NoiseProfile, NoiseChannels, DepolarizingNoise
from machq.types import Qubit


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

    @classmethod
    def from_stim(cls, stim_circuit: stim.Circuit):
        empty_circuit = cls()
        empty_circuit.circuit.append_from_stim_program_text(
            stim_program_text=str(stim_circuit)
        )

        return empty_circuit

    def __repr__(self):
        return self.circuit.__repr__()

    def __str__(self):
        return self.circuit.__str__()

    def __getitem__(self, index):
        return self.circuit[index]

    def __len__(self):
        return len(self.circuit)

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
        self.valid_qubits = len(qubit_coords)
        for idx, qcoord in enumerate(qubit_coords):
            self.circuit.append("QUBIT_COORDS", idx, qcoord)
            self.idling_qubits[idx] = 0

    def get_qubit_index(self, qubit: Qubit):
        """Given an input qubit coordinate,
        find the index of the qubit in the stim circuit.

        Parameters
        ----------
        qubit : Qubit
            The qubit coordinate to find the index for.
        """
        qubit_indices = [
            line.targets_copy()[0].value
            for line in self.circuit
            if line.name == "QUBIT_COORDS" and line.gate_args_copy() == list(qubit)
        ]
        return qubit_indices

    def qubit_map(self, qubits: List[Qubit]) -> List[int]:
        """Given a list of input qubit coordinates,
        return their respective indices in the same order.

        Parameters
        ----------
        qubits : List[Qubit]
            List of qubit coordinates

        Returns
        -------
        List[int]
            List of qubit indices
        """
        indices = []
        for qubit in qubits:
            indices += self.get_qubit_index(qubit)
        return indices

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

        if not all(x < self.valid_qubits for x in qubits):
            raise ValueError(f"Not all qubit(s) {qubits} are present in the circuit.")

    def CX(self, qubits: List[Qubit]):
        """A convenience function that streamlines the use of
        a CNOT gate in stim.

        Parameters
        ----------
        qubits : List[Qubit]
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
        terminating.
        """
        stim_string, noise_param = idle_noise
        if any(idling == 0 for _, idling in self.idling_qubits.items()):
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
        for qub in qubits:
            self.idling_qubits[qub] = 1

    def measure_qubits(self, qubits: List[int]):
        """Measure qubits in the Z basis.

        Parameters
        ----------
        qubits : List[int]
            List of qubits to measure.
        """
        self.circuit.append("M", targets=qubits, arg=self.measurement_flip_prob)
        for qub in qubits:
            self.idling_qubits[qub] = 1

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
