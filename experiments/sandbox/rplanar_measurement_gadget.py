import stim
from machq.noise import DepolarizingNoise
from machq.codes import RotatedPlanarCodeFlags

if __name__ == "__main__":
    d = 5
    code = RotatedPlanarCodeFlags(
        x_distance=d, z_distance=d, noise_profile=DepolarizingNoise(p=0.001)
    )
    code.encode_logical_zero()
    code.syndrome_extraction()
    # print(code.circuit)

    # print(
    #     f"Data qubits : {code.circuit.qubit_map(code.data_qubits)} |"
    #     f" Total: {len(code.circuit.qubit_map(code.data_qubits))}",
    # )
    # print(
    #     f"Auxil qubits : {code.circuit.qubit_map(code.auxiliary_qubits)} |"
    #     f" Total: {len(code.circuit.qubit_map(code.auxiliary_qubits))}",
    # )

    # print(
    #     f"Flag qubits : {code.circuit.qubit_map(code.flag_qubits)} |"
    #     f" Total: {len(code.circuit.qubit_map(code.flag_qubits))}",
    # )

    dem = code.circuit.as_stim.detector_error_model(
        approximate_disjoint_errors=True,
        decompose_errors=True,
        ignore_decomposition_failures=True,
    )

    # print(f"Shortest logical: {len(code.circuit.as_stim.shortest_graphlike_error())}")

    for entry in dem:
        if (
            len(entry.targets_copy()) > 2
            and not stim.target_separator() in entry.targets_copy()
            and not any(x.is_logical_observable_id() for x in entry.targets_copy())
        ):
            print(entry)
    exit()
