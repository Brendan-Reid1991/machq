from typing import List, Tuple
import itertools

from machq.types import Circuit, Qubit, Distance
from machq.codes import QuantumErrorCorrectionCode
from machq.noise import NoiseProfile, DepolarizingNoise, NoiseChannels


class RotatedPlanarCode(QuantumErrorCorrectionCode):
    r"""A class to implement a rotated planar code in stim.

    A code defined with (x_distance, z_distance) will have a coordinate grid spanning a
    (2 * x_distance + 1, 2 * z_distance + 1) space.

    Qubit layout and co-ordinates are as shown for a 3x3 code here:


    6├                            /   X   \
     │                          /           \
    5├         / ○ ----------- ○ ----------- ○
     │       /   │             │             │
    4├    Z      │      X      │      Z      │
     │       \   │             │             │
    3├         \ ○ ----------- ○ ----------- ○ \
     │           │             │             │   \
    2├           │      Z      │      X      │      Z
     │           │             │             │   /
    1├           ○ ----------- ○ ----------- ○ /
     │            \           /
    0├              \   X   /
     │
     └----┴------┴------┴------┴------┴------┴------┴
          0      1      2      3      4      5      6


    And the qubit indices:

    6├                            /  16  \
     │                          /           \
    5├         / 13 ---------- 14 ---------- 15
     │       /   │             │             │
    4├     10    │     11      │     12      │
     │       \   │             │             │
    3├         \ 7 ----------- 8 ----------- 9 \
     │           │             │             │   \
    2├           │      4      │      5      │      6
     │           │             │             │   /
    1├           1 ----------- 2 ----------- 3 /
     │            \           /
    0├              \   0   /
     │
     └----┴------┴------┴------┴------┴------┴------┴
          0      1      2      3      4      5      6
    """

    name = "rotated_planar"

    def __init__(
        self,
        x_distance: Distance = 3,
        z_distance: Distance = 3,
        noise_profile: NoiseProfile = DepolarizingNoise(p=0),
    ):
        super().__init__(
            x_distance=x_distance, z_distance=z_distance, noise_profile=noise_profile
        )
        self.x_dim = 2 * z_distance + 1
        self.y_dim = 2 * x_distance + 1

        self.data_qubits = self._define_data_()

        self.x_auxiliary_qubits, self.z_auxiliary_qubits = self._define_auxiliary_()

        self.auxiliary_qubits = self.x_auxiliary_qubits + self.z_auxiliary_qubits

        self.qubit_coords = sorted(
            self.data_qubits + self.auxiliary_qubits,
            key=lambda x: [x[1], x[0]],
        )

        self.circuit.add_qubits(qubit_coords=self.qubit_coords)

        self.qubit_map = {qubit: idx for idx, qubit in enumerate(self.qubit_coords)}
        # Could this map live in the Circuit class?

        self.plaquette_corners = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def __str__(self) -> str:
        return f"{self.name}_{self.x_distance}x{self.z_distance}"

    def _define_data_(self):
        return [
            Qubit(_x, _y)
            for _y in range(1, self.y_dim, 2)
            for _x in range(1, self.x_dim, 2)
        ]

    def _define_auxiliary_(self):
        x_auxiliary_qubits = []
        z_auxiliary_qubits = []

        # X-Auxiliary Qubit Coordinates
        offset = 0
        for x in range(2, (self.x_dim - 1), 2):
            ylow = 0 + 2 * (offset % 2)
            yhigh = self.y_dim + (1 - self.x_distance % 2)
            for y in range(ylow, yhigh, 4):
                x_auxiliary_qubits.append(Qubit(x, y))
            offset += 1
        # Z-Auxiliary Qubit Coordinates
        offset = 1
        for y in range(2, self.y_dim - 1, 2):
            xlow = 0 + 2 * (offset % 2)
            xhigh = self.x_dim
            for x in range(xlow, xhigh, 4):
                z_auxiliary_qubits.append(Qubit(x, y))
            offset += 1
        return x_auxiliary_qubits, z_auxiliary_qubits

    def _neighbouring_data_qubits(self, auxiliary_qubit: Qubit):
        """Check which data qubits are neighbouring the input auxiliary qubit.

        Parameters
        ----------
        auxiliary_qubit : Qubit
            An auxiliary qubit coordinate.
        """
        if not auxiliary_qubit in self.auxiliary_qubits:
            raise ValueError("Qubit is not an auxiliary qubit.")

        return (
            auxiliary_qubit + delta
            for delta in self.plaquette_corners
            if auxiliary_qubit + delta in self.data_qubits
        )

    def time_step(self):
        """Add a time step to the circuit."""
        self.circuit.time_step(idle_noise=self.noise_profile.idle_noise)

    def _measure_syndromes_(
        self,
        x_schedule: List[Tuple[int, int]] = None,
        z_schedule: List[Tuple[int, int]] = None,
    ):
        """A function describing syndrome extraction in the rotated planar code."""

        x_schedule = (
            x_schedule
            if x_schedule is not None
            else [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        )

        z_schedule = (
            z_schedule
            if z_schedule is not None
            else [(-1, 1), (-1, -1), (1, 1), (1, -1)]
        )

        self.circuit.H([self.qubit_map[x_aux] for x_aux in self.x_auxiliary_qubits])

        self.time_step()

        for idx, (x_delta, z_delta) in enumerate(zip(x_schedule, z_schedule)):
            cnot_qubits = []
            for qubit in self.auxiliary_qubits:
                if (
                    qubit in self.x_auxiliary_qubits
                    and qubit + x_delta in self.data_qubits
                ):
                    cnot_qubits.append(qubit)
                    cnot_qubits.append(qubit + x_delta)
                if (
                    qubit in self.z_auxiliary_qubits
                    and qubit + z_delta in self.data_qubits
                ):
                    cnot_qubits.append(qubit + z_delta)
                    cnot_qubits.append(qubit)

            cnot_qubit_indices = [self.qubit_map[x] for x in cnot_qubits]
            self.circuit.CX(cnot_qubit_indices)
            self.time_step()

        self.circuit.H([self.qubit_map[x_aux] for x_aux in self.x_auxiliary_qubits])

        self.time_step()

        self.circuit.measure_qubits(
            qubits=[self.qubit_map[aux] for aux in self.auxiliary_qubits],
        )

        self.time_step()

        self.circuit.reset_qubits(
            qubits=[self.qubit_map[aux] for aux in self.auxiliary_qubits]
        )

    def encode_logical_zero(self):
        """Encode the logical zero state.
        This is done by resetting all qubits, and performing
        one round of syndrome extraction. The auxiliary qubits are
        measured at the end of the round, and the Z-auxiliary
        qubits define the deterministic detectors.
        """
        noise_channel: Callable = self.noise_profile.noise_channels.XError
        noise_param = self.noise_profile.reset_noise

        self.circuit.reset_qubits()
        self.time_step()

        self._measure_syndromes_()

        max_lookback = len(self.z_auxiliary_qubits)
        lookback_and_arguments = [
            ([-max_lookback + idx], (z_aux.x, z_aux.y, 0))
            for idx, z_aux in enumerate(self.z_auxiliary_qubits)
        ]

        self.circuit.detectors(lookbacks_and_args=lookback_and_arguments)

    def encode_logical_plus(self):
        """Encode the logical plus state.
        This is done by resetting all qubits, applying Hadamard
        gates to the data qubits and performing one round of
        syndrome extraction. The auxiliary qubits are
        measured at the end of the round, and the Z-auxiliary
        qubits define the deterministic detectors.
        """
        noise_channel: Callable = self.noise_profile.noise_channels.XError
        noise_param = self.noise_profile.reset_noise

        self.circuit.reset_qubits()
        self.circuit.H([self.qubit_map[x] for x in self.data_qubits])

        self._measure_syndromes_()

        max_lookback = len(self.auxiliary_qubits)
        lookback_and_arguments = [
            ([-max_lookback + idx], (x_aux.x, x_aux.y, 0))
            for idx, x_aux in enumerate(self.x_auxiliary_qubits)
        ]

        self.circuit.detectors(lookbacks_and_args=lookback_and_arguments)

    def syndrome_extraction(self, rounds: int = None):
        """Perform multiple rounds of error correction.

        Parameters
        ----------
        rounds : int, optional
            How many rounds of syndrome extraction to perform, by default None.
            If None, the minimum between (x_distance, z_distance) is taken.
        """
        rounds = min(self.x_distance, self.z_distance) if rounds is None else rounds

        max_lookback = len(self.auxiliary_qubits)
        for _r in range(1, rounds):
            self._measure_syndromes_()

            lookbacks_and_arguments = [
                (
                    [-max_lookback + idx, -2 * max_lookback + idx],
                    (aux.x, aux.y, _r),
                )
                for idx, aux in enumerate(self.auxiliary_qubits)
            ]
            self.circuit.detectors(lookbacks_and_args=lookbacks_and_arguments)

    def measure_data_qubits_for_z_memory(self):
        """Measure out the data qubits and apply the relevant
        detectors for a logical Z memory experiment.
        """
        self.circuit.measure_qubits(
            qubits=[self.qubit_map[qub] for qub in self.data_qubits]
        )

        max_lookback = len(self.data_qubits) + len(self.z_auxiliary_qubits)
        data_lookback = len(self.data_qubits)
        lookback_and_args = []

        for idx, z_aux in enumerate(self.z_auxiliary_qubits):
            _lookback_ = [
                -data_lookback + dq_idx
                for dq_idx, dq in enumerate(self.data_qubits)
                if dq in self._neighbouring_data_qubits(auxiliary_qubit=z_aux)
            ] + [-max_lookback + idx]

            lookback_and_args.append((_lookback_, (z_aux.x, z_aux.y, self.z_distance)))

        self.circuit.detectors(lookbacks_and_args=lookback_and_args)

    def measure_data_qubits_for_x_memory(self):
        """Measure out the data qubits and apply the relevant
        detectors for a logical X memory experiment.
        """
        self.circuit.H(qubits=[self.qubit_map[qub] for qub in self.data_qubits])
        self.time_step()
        self.circuit.measure_qubits(
            qubits=[self.qubit_map[qub] for qub in self.data_qubits]
        )

        max_lookback = len(self.data_qubits) + len(self.auxiliary_qubits)
        data_lookback = len(self.data_qubits)
        lookback_and_args = []

        for idx, x_aux in enumerate(self.x_auxiliary_qubits):
            _lookback_ = [
                -data_lookback + dq_idx
                for dq_idx, dq in enumerate(self.data_qubits)
                if dq in self._neighbouring_data_qubits(auxiliary_qubit=x_aux)
            ] + [-max_lookback + idx]

            lookback_and_args.append((_lookback_, (x_aux.x, x_aux.y, self.x_distance)))

        self.circuit.detectors(lookbacks_and_args=lookback_and_args)

    def logical_z_memory(self, rounds: int = None):
        """Encode a logical zero state and maintain it for
        rounds of error correction.

        Parameters
        ----------
        rounds : int, optional
            How many rounds to maintain the logical zero state for, by default None.
            If None, the value of z_distance is taken.
        """
        rounds = self.z_distance if rounds is None else rounds
        self.encode_logical_zero()

        self.syndrome_extraction(rounds=rounds)

        self.measure_data_qubits_for_z_memory()

        lookback = len(self.data_qubits)
        logical_indices = [
            -lookback + idx
            for idx, qub in enumerate(self.data_qubits)
            if qub.y == self.y_dim - 2
        ]
        self.circuit.add_logical(indices=logical_indices)

    def logical_x_memory(self, rounds: int = None):
        """Encode a logical plus state and maintain it for
        rounds of error correction.

        Parameters
        ----------
        rounds : int, optional
            How many rounds to maintian the logical plus state for, by default None.
            If None, the value of x_distance is taken.
        """
        rounds = self.x_distance if rounds is None else rounds
        self.encode_logical_plus()

        self.syndrome_extraction(rounds=rounds)

        self.measure_data_qubits_for_x_memory()

        lookback = len(self.data_qubits)
        logical_indices = [
            -lookback + idx
            for idx, qub in enumerate(self.data_qubits)
            if qub.x == self.x_dim - 2
        ]
        self.circuit.add_logical(indices=logical_indices)
