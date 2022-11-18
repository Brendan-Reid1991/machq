import stim
from machq.noise import DepolarizingNoise
from machq.codes import RotatedPlanarCodeGadget

if __name__ == "__main__":
    d = 13
    code = RotatedPlanarCodeGadget(
        x_distance=d, z_distance=d, noise_profile=DepolarizingNoise(p=0.001)
    )
    import time as time

    start = time.time()
    code.logical_x_memory()
    end = time.time()
    print(end - start)
    # print(code.circuit)

    # dem = code.circuit.as_stim.detector_error_model(
    #     approximate_disjoint_errors=True,
    #     decompose_errors=True,
    #     ignore_decomposition_failures=False,
    # )

    # print(f"Shortest logical: {len(code.circuit.as_stim.shortest_graphlike_error())}")

    # for entry in dem:
    #     if (
    #         len(entry.targets_copy()) > 2
    #         and not stim.target_separator() in entry.targets_copy()
    #         and not any(x.is_logical_observable_id() for x in entry.targets_copy())
    #     ):
    #         print(entry)
    # exit()
