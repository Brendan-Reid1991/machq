from machq.types import Circuit


class RotatedPlanarCode:
    r"""A class to implement a rotated
    planar code in stim.

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
        self, x_distance: int = 3, z_distance: int = 3, circuit: Circuit = Circuit()
    ):
        self.x_distance = x_distance
        self.z_distance = z_distance
        self.x_dim = 2 * z_distance + 1
        self.y_dim = 2 * x_distance + 1

        self.circuit = circuit

        self.data_qubits = [
            (_x, _y) for _y in range(1, self.y_dim, 2) for _x in range(1, self.x_dim, 2)
        ]

        self.x_auxiliary_qubits = []
        self.z_auxiliary_qubits = []

        # X stabilisers
        offset = 0
        for x in range(2, (self.x_dim - 1), 2):
            ylow = 0 + 2 * (offset % 2)
            yhigh = self.y_dim + (1 - self.x_distance % 2)
            for y in range(ylow, yhigh, 4):
                self.x_auxiliary_qubits.append((x, y))
            offset += 1

        # Z stabilisers
        offset = 1
        for y in range(2, self.y_dim - 1, 2):
            xlow = 0 + 2 * (offset % 2)
            xhigh = self.x_dim
            for x in range(xlow, xhigh, 4):
                self.z_auxiliary_qubits.append((x, y))
            offset += 1

        self.auxiliary_qubits = self.x_auxiliary_qubits + self.z_auxiliary_qubits

        self.qubit_coords = sorted(
            self.data_qubits + self.auxiliary_qubits,
            key=lambda x: [x[1], x[0]],
        )

        self.circuit.add_qubits(qubit_coords=self.qubit_coords)

    def __str__(self) -> str:
        return f"{self.name}_{self.x_distance}x{self.z_distance}"
