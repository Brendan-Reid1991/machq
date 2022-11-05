from machq.decoders.get_logical_errors import count_logical_errors
from machq.codes import RotatedPlanarCode
from machq.noise import DepolarizingNoise

num_shots = 1e4
for distance in [3, 5, 7, 9]:
    code = RotatedPlanarCode(
        x_distance=distance,
        z_distance=distance,
        noise_profile=DepolarizingNoise(p=1e-3),
    )
    code.logical_z_memory()
    stim_circuit = code.circuit.as_stim
    print(count_logical_errors(data_circuit=stim_circuit, num_shots=num_shots))
