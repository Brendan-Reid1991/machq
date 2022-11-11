import stim

circ = stim.Circuit(
    """QUBIT_COORDS(2, 0) 0
QUBIT_COORDS(1, 1) 1
QUBIT_COORDS(3, 1) 2
QUBIT_COORDS(5, 1) 3
QUBIT_COORDS(2, 2) 4
QUBIT_COORDS(4, 2) 5
QUBIT_COORDS(6, 2) 6
QUBIT_COORDS(1, 3) 7
QUBIT_COORDS(3, 3) 8
QUBIT_COORDS(5, 3) 9
QUBIT_COORDS(0, 4) 10
QUBIT_COORDS(2, 4) 11
QUBIT_COORDS(4, 4) 12
QUBIT_COORDS(1, 5) 13
QUBIT_COORDS(3, 5) 14
QUBIT_COORDS(5, 5) 15
QUBIT_COORDS(4, 6) 16
R 1 2 3 7 8 9 13 14 15
PAULI_CHANNEL_1(0.01, 0, 0) 1 2 3 7 8 9 13 14 15
R 0 11 5 16 4 6 10 12
PAULI_CHANNEL_1(0.01, 0, 0) 0 11 5 16 4 6 10 12
TICK
H 0 11 5 16
DEPOLARIZE1(0.01) 0 11 5 16 1 2 3 4 6 7 8 9 10 12 13 14 15
TICK
CX 0 1 11 13 5 8 7 4 9 6 14 12
DEPOLARIZE2(0.01) 0 1 11 13 5 8 7 4 9 6 14 12
DEPOLARIZE1(0.01) 2 3 10 15 16
TICK
CX 0 2 11 14 5 9 1 4 3 6 8 12
DEPOLARIZE2(0.01) 0 2 11 14 5 9 1 4 3 6 8 12
DEPOLARIZE1(0.01) 7 10 13 15 16
TICK
CX 11 7 5 2 16 14 8 4 13 10 15 12
DEPOLARIZE2(0.01) 11 7 5 2 16 14 8 4 13 10 15 12
DEPOLARIZE1(0.01) 0 1 3 6 9
TICK
CX 11 8 5 3 16 15 2 4 7 10 9 12
DEPOLARIZE2(0.01) 11 8 5 3 16 15 2 4 7 10 9 12
DEPOLARIZE1(0.01) 0 1 6 13 14
TICK
H 0 11 5 16
DEPOLARIZE1(0.01) 0 11 5 16 1 2 3 4 6 7 8 9 10 12 13 14 15
TICK
M(0.01) 0 11 5 16 4 6 10 12
DEPOLARIZE1(0.01) 1 2 3 7 8 9 13 14 15
TICK
DETECTOR(2, 2, 0) rec[-4]
DETECTOR(6, 2, 0) rec[-3]
DETECTOR(0, 4, 0) rec[-2]
DETECTOR(4, 4, 0) rec[-1]
R 0 11 5 16 4 6 10 12
PAULI_CHANNEL_1(0.01, 0, 0) 0 11 5 16 4 6 10 12
DEPOLARIZE1(0.01) 1 2 3 7 8 9 13 14 15
TICK
H 0 11 5 16
DEPOLARIZE1(0.01) 0 11 5 16 1 2 3 4 6 7 8 9 10 12 13 14 15
TICK
CX 0 1 11 13 5 8 7 4 9 6 14 12
DEPOLARIZE2(0.01) 0 1 11 13 5 8 7 4 9 6 14 12
DEPOLARIZE1(0.01) 2 3 10 15 16
TICK
CX 0 2 11 14 5 9 1 4 3 6 8 12
DEPOLARIZE2(0.01) 0 2 11 14 5 9 1 4 3 6 8 12
DEPOLARIZE1(0.01) 7 10 13 15 16
TICK
CX 11 7 5 2 16 14 8 4 13 10 15 12
DEPOLARIZE2(0.01) 11 7 5 2 16 14 8 4 13 10 15 12
DEPOLARIZE1(0.01) 0 1 3 6 9
TICK
CX 11 8 5 3 16 15 2 4 7 10 9 12
DEPOLARIZE2(0.01) 11 8 5 3 16 15 2 4 7 10 9 12
DEPOLARIZE1(0.01) 0 1 6 13 14
TICK
H 0 11 5 16
DEPOLARIZE1(0.01) 0 11 5 16 1 2 3 4 6 7 8 9 10 12 13 14 15
TICK
M(0.01) 0 11 5 16 4 6 10 12
DETECTOR(2, 0, 1) rec[-8] rec[-16]
DETECTOR(2, 4, 1) rec[-7] rec[-15]
DETECTOR(4, 2, 1) rec[-6] rec[-14]
DETECTOR(4, 6, 1) rec[-5] rec[-13]
DETECTOR(2, 2, 1) rec[-4] rec[-12]
DETECTOR(6, 2, 1) rec[-3] rec[-11]
DETECTOR(0, 4, 1) rec[-2] rec[-10]
DETECTOR(4, 4, 1) rec[-1] rec[-9]
DEPOLARIZE1(0.01) 1 2 3 7 8 9 13 14 15
TICK
R 0 11 5 16 4 6 10 12
PAULI_CHANNEL_1(0.01, 0, 0) 0 11 5 16 4 6 10 12
DEPOLARIZE1(0.01) 1 2 3 7 8 9 13 14 15
TICK
H 0 11 5 16
DEPOLARIZE1(0.01) 0 11 5 16 1 2 3 4 6 7 8 9 10 12 13 14 15
TICK
CX 0 1 11 13 5 8 7 4 9 6 14 12
DEPOLARIZE2(0.01) 0 1 11 13 5 8 7 4 9 6 14 12
DEPOLARIZE1(0.01) 2 3 10 15 16
TICK
CX 0 2 11 14 5 9 1 4 3 6 8 12
DEPOLARIZE2(0.01) 0 2 11 14 5 9 1 4 3 6 8 12
DEPOLARIZE1(0.01) 7 10 13 15 16
TICK
CX 11 7 5 2 16 14 8 4 13 10 15 12
DEPOLARIZE2(0.01) 11 7 5 2 16 14 8 4 13 10 15 12
DEPOLARIZE1(0.01) 0 1 3 6 9
TICK
CX 11 8 5 3 16 15 2 4 7 10 9 12
DEPOLARIZE2(0.01) 11 8 5 3 16 15 2 4 7 10 9 12
DEPOLARIZE1(0.01) 0 1 6 13 14
TICK
H 0 11 5 16
DEPOLARIZE1(0.01) 0 11 5 16 1 2 3 4 6 7 8 9 10 12 13 14 15
TICK
M(0.01) 0 11 5 16 4 6 10 12
DETECTOR(2, 0, 2) rec[-8] rec[-16]
DETECTOR(2, 4, 2) rec[-7] rec[-15]
DETECTOR(4, 2, 2) rec[-6] rec[-14]
DETECTOR(4, 6, 2) rec[-5] rec[-13]
DETECTOR(2, 2, 2) rec[-4] rec[-12]
DETECTOR(6, 2, 2) rec[-3] rec[-11]
DETECTOR(0, 4, 2) rec[-2] rec[-10]
DETECTOR(4, 4, 2) rec[-1] rec[-9]
DEPOLARIZE1(0.01) 1 2 3 7 8 9 13 14 15
TICK
M(0.01) 1 2 3 7 8 9 13 14 15
DEPOLARIZE1(0.01) 0 4 5 6 10 11 12 16
TICK
DETECTOR(2, 2, 3) rec[-13] rec[-9] rec[-8] rec[-6] rec[-5]
DETECTOR(6, 2, 3) rec[-12] rec[-7] rec[-4]
DETECTOR(0, 4, 3) rec[-11] rec[-6] rec[-3]
DETECTOR(4, 4, 3) rec[-10] rec[-5] rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-3] rec[-2] rec[-1]"""
)

import sinter

surface_code_tasks = [
    sinter.Task(
        circuit=stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            rounds=d * 3,
            distance=d,
            after_clifford_depolarization=noise,
            after_reset_flip_probability=noise,
            before_measure_flip_probability=noise,
            before_round_data_depolarization=noise,
        ),
        json_metadata={"d": d, "r": d * 3, "p": noise},
    )
    for d in [3, 5, 7]
    for noise in [0.008, 0.009, 0.01, 0.011, 0.012]
]

collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
    num_workers=4,
    tasks=surface_code_tasks,
    decoders=["pymatching"],
    max_shots=1_00_000,
    max_errors=5_000,
    print_progress=True,
)


fig, ax = plt.subplots(1, 1)
sinter.plot_error_rate(
    ax=ax,
    stats=collected_surface_code_stats,
    x_func=lambda stats: stats.json_metadata["p"],
    group_func=lambda stats: stats.json_metadata["d"],
    failure_units_per_shot_func=lambda stats: stats.json_metadata["r"],
)
ax.set_ylim(5e-3, 5e-2)
ax.set_xlim(0.008, 0.012)
ax.loglog()
ax.set_title("Surface Code Error Rates per Round under Circuit Noise")
ax.set_xlabel("Phyical Error Rate")
ax.set_ylabel("Logical Error Rate per Round")
ax.grid(which="major")
ax.grid(which="minor")
plt.savefig("test.png", bbox_inches="tight")
