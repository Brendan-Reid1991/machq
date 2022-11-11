import stim
import sinter

from machq.analysis.evaluate_failures import logical_failure_probability
from machq.codes import RotatedPlanarCode
from machq.noise import CircuitLevelNoise

num_shots = 1e5
for distance in [3, 5, 7, 9]:
    code = RotatedPlanarCode(
        x_distance=distance,
        z_distance=distance,
        noise_profile=CircuitLevelNoise(p=1e-3),
    )
    code.logical_z_memory()
    stim_circuit = code.circuit.as_stim
    print(logical_failure_probability(circuit=stim_circuit, num_shots=num_shots))
