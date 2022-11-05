from typing import List, Tuple

from machq.types import Circuit, Qubit
from machq.noise import NoiseProfile, DepolarizingNoise


class RotatedPlanarCode:
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
        x_distance: int = 3,
        z_distance: int = 3,
        noise_profile: NoiseProfile = DepolarizingNoise(p=0),
    ):
        self.x_distance = x_distance
        self.z_distance = z_distance
        self.x_dim = 2 * z_distance + 1
        self.y_dim = 2 * x_distance + 1

        self.circuit = Circuit()
        self.noise_profile = noise_profile

        self.data_qubits = [
            Qubit(_x, _y)
            for _y in range(1, self.y_dim, 2)
            for _x in range(1, self.x_dim, 2)
        ]

        self.x_auxiliary_qubits = []
        self.z_auxiliary_qubits = []

        # X-Auxiliary Qubit Coordinates
        offset = 0
        for x in range(2, (self.x_dim - 1), 2):
            ylow = 0 + 2 * (offset % 2)
            yhigh = self.y_dim + (1 - self.x_distance % 2)
            for y in range(ylow, yhigh, 4):
                self.x_auxiliary_qubits.append(Qubit(x, y))
            offset += 1

        # Z-Auxiliary Qubit Coordinates
        offset = 1
        for y in range(2, self.y_dim - 1, 2):
            xlow = 0 + 2 * (offset % 2)
            xhigh = self.x_dim
            for x in range(xlow, xhigh, 4):
                self.z_auxiliary_qubits.append(Qubit(x, y))
            offset += 1

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

    def syndrome_extraction(
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
            else [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        )

        for x_aux in self.x_auxiliary_qubits:
            self.circuit.H(self.qubit_map[x_aux])

        self.time_step()

        for idx, (x_delta, z_delta) in enumerate(zip(x_schedule, z_schedule)):
            controls = []
            targets = []
            for qubit in self.auxiliary_qubits:
                if (
                    qubit in self.x_auxiliary_qubits
                    and qubit + x_delta in self.data_qubits
                ):
                    controls.append(qubit)
                    targets.append(qubit + x_delta)
                if (
                    qubit in self.z_auxiliary_qubits
                    and qubit + z_delta in self.data_qubits
                ):
                    controls.append(qubit + z_delta)
                    targets.append(qubit)
            for ctrl, targ in zip(controls, targets):
                self.circuit.CX(self.qubit_map[ctrl], self.qubit_map[targ])
            self.time_step()

        for x_aux in self.x_auxiliary_qubits:
            self.circuit.H(self.qubit_map[x_aux])

        self.time_step()

    def encode_logical_zero(self):
        """Encode the logical zero state.
        This is done by resetting all qubits, and performing
        one round of syndrome extraction. The auxiliary qubits are
        measured at the end of the round, and the Z-auxiliary
        qubits define the deterministic detectors.
        """
        noise_channel: Callable = self.noise_profile.noise_channels.XError
        noise_param = self.noise_profile.reset_noise

        self.circuit.reset_qubits(reset_noise=noise_channel(noise_param))

        self.syndrome_extraction()

        self.circuit.measure_qubits(
            measurement_flip=self.noise_profile.measurement_flip_prob,
            qubits=[self.qubit_map[aux] for aux in self.auxiliary_qubits],
        )

        max_lookback = len(self.z_auxiliary_qubits)
        lookback_indices = []
        arguments = []
        for idx, z_aux in enumerate(self.z_auxiliary_qubits):
            lookback_indices.append(-max_lookback + idx)
            arguments.append((z_aux.x, z_aux.y, 0))

        self.circuit.detectors(lookback_indices=lookback_indices, arguments=arguments)

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

        self.circuit.reset_qubits(reset_noise=noise_channel(noise_param))
        for qubit in self.data_qubits:
            self.circuit.H(self.qubit_map[qubit])

        self.syndrome_extraction()

        self.circuit.measure_qubits(
            measurement_flip=self.noise_profile.measurement_flip_prob,
            qubits=[self.qubit_map[aux] for aux in self.auxiliary_qubits],
        )

        max_lookback = len(self.z_auxiliary_qubits)
        lookback_indices = []
        arguments = []
        for idx, z_aux in enumerate(self.z_auxiliary_qubits):
            lookback_indices.append(-max_lookback + idx)
            arguments.append((z_aux.x, z_aux.y, 0))

        self.circuit.detectors(lookback_indices=lookback_indices, arguments=arguments)


if __name__ == "__main__":
    code = RotatedPlanarCode()
    code.encode_logical_zero()
    print(code.circuit)
