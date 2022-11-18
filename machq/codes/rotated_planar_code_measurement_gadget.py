from typing import List, Tuple
import itertools

from machq.types import Circuit, Qubit, Distance
from machq.codes import QuantumErrorCorrectionCode
from machq.noise import NoiseProfile, DepolarizingNoise, NoiseChannels


class RotatedPlanarCodeGadget(QuantumErrorCorrectionCode):
    r"""A class to implement a rotated planar code in stim.
    The stabilisers in this construction consist of two ancilla qubits,
    in order to mitigate against measurement noise specifically. This is known as a "measurement gadget". The coordinate grid is defined similarly
    to the standard RPlanar code, as below.

    A code defined with (x_distance, z_distance) will have a coordinate grid spanning a
    (2 * x_distance + 1, 2 * z_distance + 1) space.

    Qubit layout and co-ordinates are as shown for a 3x3 code here:


    6├                            / XA XB \
     │                          /           \
    5├         / ○ ----------- ○ ----------- ○
     │       /   │             │             │
    4├  ZA ZB    │    XA XB    │    ZA ZB    │
     │       \   │             │             │
    3├         \ ○ ----------- ○ ----------- ○ \
     │           │             │             │   \
    2├           │    ZA ZB    │    XA XB    │   ZA ZB
     │           │             │             │   /
    1├           ○ ----------- ○ ----------- ○ /
     │            \           /
    0├              \ XA XB /
     │
     └----┴------┴------┴------┴------┴------┴------┴
          0      1      2      3      4      5      6


    As mentioned, each stabiliser (plaquette) consists of two qubits, rather than one.
    The ancilla qubits "share coordinates" in some sense, such that each AB pair is given coordinates (x, y) and (x+0.5, y+0.5) respectively.

    Above, the AB pairs are laid out beside each other and we will maintain
    that representation, although it is not representative of qubit connectivity.

    Stabiliser layout is as below. Empty squares represent A-ancillae qubits
    and filled squares represent B-ancillae.

            ○ ----------- ○
            │             │
            │    ◻︎ - ◼︎    │
            │             │
            ○ ----------- ○

    These qubits are entangled using a "Ancilla encoding" cirucit. We start with the case of X-stabilisers (detecting Z-errors) and then generalise to Z-stabilisers.
             ┌───┐
    ◻︎ : |0> ─┤ H ├──■──
             └───┘┌─┴─┐
    ◼︎ : |0> ──────┤ X ├
                  └───┘
    This puts the pair into a Bell stage |ϕ+> = |00> + |11>.
    The pair then share the weight four stabiliser, each taking part in two CNOTS (schedule given below). In the presence of data qubit errors, the AB pair will be in one of |ϕ±> = |00> ± |11>.

    We want these states to be mapped to
    |ϕ+> ---> |00>
    |ϕ-> ---> |11>

    For this we use an "ancilla decoding circuit", given by:
               ┌───┐
    ◻︎ :  ──■───┤ H ├──■─── MZ
         ┌─┴─┐ └───┘┌─┴─┐
    ◼︎ :  ┤ X ├──────┤ X ├─ MZ
         └───┘      └───┘

    Where MZ here means we measure in the Z-basis.

    For Z-stabilisers, we need a Bell state that detects X-errors. Naturally,
    this is achieved by |++> + |--> . This can be achieved with the same encoding circuit given above. At the end of the stabiliser measurement however, the AB pair is in one of |ψ±> = |++> ± |-->.
    By applying Hadamards to both A and B ancillae, we find:
    H0 H1 |ψ±> = |ϕ±>.

    As such then, the "ancilla decoding circuit" for Z-stabilisers is the same
    as for X-stabilisers, but with Hadamards applied to both qubits prior.

    We will begin by assuming that the schedule for each stabiliser is the same
    as in the absence of B ancillae. That is, for X stabilisers we use a "Z" schedule, and for Z stabilisers we use a "backwards N" schedule:

            ○ ----------- ○ ----------- ○
            │  1       2  │  1       3  │
            │      X      │      Z      │
            │  3       4  │  2       4  │
            ○ ----------- ○ ----------- ○

    Where here the numbers represent the time step.

    We are maintaining that schedule, however we have a number of
    different options for which auxiliary qubit takes part in which
    timestep. Two arrangements are shown below. For both the X (left)
    and Z (right) stabiliser, this is an AABB arrangement.

            ○ ----------- ○ ----------- ○
            │  1 - ◻︎ - 2  │  1 ┐   ┌ 3  │
            │      |      │    ◻︎ - ◼︎    │
            │  3 - ◼︎ - 4  │  2 ┘   └ 4  │
            ○ ----------- ○ ----------- ○

    Similarly, we can choose an ABAB arrangement by swapping these:

             ○ ----------- ○----------- ○
             │  1 ┐   ┌ 2  │ 1 - ◻︎ - 3  |
             │    ◻︎ - ◼︎    │     |      |
             │  3 ┘   └ 4  │ 2 - ◼ - 4  |
             ○ ----------- ○ -----------○

    There is a third possibility, ABBA, which requires greater connectivity.

    """

    name = "rotated_planar_measurement_gadget"

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

        self.x_flags, self.z_flags = self._define_flags_()
        self.flag_qubits = self.x_flags + self.z_flags

        self.qubit_coords = sorted(
            self.data_qubits + self.auxiliary_qubits + self.flag_qubits,
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

    def _define_flags_(self):
        """Get flag qubits for each plaquette."""
        x_flags = [Qubit(0.5, 0.5) + qubit for qubit in self.x_auxiliary_qubits]
        z_flags = [Qubit(0.5, 0.5) + qubit for qubit in self.z_auxiliary_qubits]

        return x_flags, z_flags

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

    def encode_flag_qubits(self):
        """Encode the auxiliary and flag qubit pairs."""
        self.circuit.reset_qubits(
            [
                self.qubit_map[qubit]
                for qubit in (self.auxiliary_qubits + self.flag_qubits)
            ]
        )
        self.time_step()
        self.circuit.H(qubits=[self.qubit_map[aux] for aux in self.auxiliary_qubits])
        self.time_step()
        self.circuit.CX(
            qubits=[
                self.qubit_map[qubit]
                for qubit in itertools.chain.from_iterable(
                    zip(self.auxiliary_qubits, self.flag_qubits)
                )
            ]
        )
        self.time_step()

    def decode_flag_qubits(self):
        """Unentangle the auxiliary and flag qubit pairs"""
        self.circuit.H(
            qubits=[
                self.qubit_map[aux] for aux in self.z_auxiliary_qubits + self.z_flags
            ]
        )

        self.time_step()

        self.circuit.CX(
            qubits=[
                self.qubit_map[qubit]
                for qubit in itertools.chain.from_iterable(
                    zip(self.auxiliary_qubits, self.flag_qubits)
                )
            ]
        )
        self.time_step()

        self.circuit.H(qubits=[self.qubit_map[aux] for aux in self.auxiliary_qubits])

        self.time_step()

        self.circuit.CX(
            qubits=[
                self.qubit_map[qubit]
                for qubit in itertools.chain.from_iterable(
                    zip(self.auxiliary_qubits, self.flag_qubits)
                )
            ]
        )
        self.time_step()

    def measure_aux_flag_pairs(self):
        """Measure all auxiliary and flag qubits, and apply the within-round
        detectors.
        """
        self.circuit.measure_qubits(
            qubits=[
                self.qubit_map[qubit]
                for qubit in self.auxiliary_qubits + self.flag_qubits
            ]
        )
        self.time_step()

    def aux_flag_detectors(self, measurement_round: int = 0):
        """Add the within-round detectors for auxiliary qubits
        and flag qubits.

        Parameters
        ----------
        measurement_round : int, optional
            Which measurement round we are currently in, by default 0
        """
        max_lookback = len(self.auxiliary_qubits + self.flag_qubits)
        flag_lookback = len(self.flag_qubits)
        lookbacks_and_args = [
            (
                (
                    [-max_lookback + idx, -flag_lookback + idx],
                    (flag.x, flag.y, measurement_round),
                )
            )
            for idx, flag in enumerate(self.flag_qubits)
        ]
        self.circuit.detectors(lookbacks_and_args=lookbacks_and_args)

    def _measure_stabilisers(
        self,
        x_schedule: List[Tuple[int, int]],
        z_schedule: List[Tuple[int, int]],
    ):
        """Measure all stabilisers in the code.

        Parameters
        ----------
        x_schedule : List[Tuple[int, int]]
            The schedule to follow for the X-stabilisers
        z_schedule : List[Tuple[int, int]]
            The schedule to follow for the Z-stabilisers
        """

        # We use these to determine if an auxiliary or flag qubit
        # is involved in this time step.

        # ABAB
        # x_flag_steps = [1, 3]
        # z_flag_steps = [1, 3]

        # AABB
        # x_flag_steps = [2, 3]
        # z_flag_steps = [2, 3]

        # ABBA
        x_flag_steps = [1, 2]
        z_flag_steps = [1, 2]

        for idx, (x_delta, z_delta) in enumerate(zip(x_schedule, z_schedule)):
            cnot_qubits = []

            for x_aux, x_flag in zip(self.x_auxiliary_qubits, self.x_flags):
                data = x_aux + x_delta
                if data in self.data_qubits:
                    ctrl = x_aux if idx not in x_flag_steps else x_flag
                    cnot_qubits += [ctrl, data]

            for z_aux, z_flag in zip(self.z_auxiliary_qubits, self.z_flags):
                data = z_aux + z_delta
                if data in self.data_qubits:
                    targ = z_aux if idx not in z_flag_steps else z_flag
                    cnot_qubits += [data, targ]

            cnot_qubit_indices = [self.qubit_map[x] for x in cnot_qubits]
            self.circuit.CX(cnot_qubit_indices)
            self.time_step()

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

        self.encode_flag_qubits()

        self._measure_stabilisers(x_schedule=x_schedule, z_schedule=z_schedule)

        self.decode_flag_qubits()

        self.measure_aux_flag_pairs()

        self.circuit.reset_qubits(
            qubits=[
                self.qubit_map[aux] for aux in self.auxiliary_qubits + self.flag_qubits
            ]
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

        self.aux_flag_detectors(measurement_round=0)

        max_lookback = len(self.z_auxiliary_qubits) + len(self.flag_qubits)
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
        self.time_step()

        self._measure_syndromes_()

        self.aux_flag_detectors(measurement_round=0)

        max_lookback = len(self.auxiliary_qubits) + len(self.flag_qubits)
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

        # Inter-round detectors are done with current round A ancillae
        # and previous round B ancillae.
        max_lookback = len(self.auxiliary_qubits) + len(self.flag_qubits)
        previous_round_lookback = max_lookback + len(self.flag_qubits)
        for _r in range(1, rounds):
            self._measure_syndromes_()

            self.aux_flag_detectors(measurement_round=_r)

            lookbacks_and_arguments = [
                (
                    [-max_lookback + idx, -previous_round_lookback + idx],
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

        ancilla_lookback = len(self.data_qubits) + len(self.z_flags)
        data_lookback = len(self.data_qubits)
        lookback_and_args = []

        for idx, z_aux in enumerate(self.z_auxiliary_qubits):
            _lookback_ = [
                -data_lookback + dq_idx
                for dq_idx, dq in enumerate(self.data_qubits)
                if dq in self._neighbouring_data_qubits(auxiliary_qubit=z_aux)
            ] + [-ancilla_lookback + idx]

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

        max_lookback = len(self.data_qubits) + len(self.flag_qubits)
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
            How many rounds to maintian the logical zero state for, by default None.
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
