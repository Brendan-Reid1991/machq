from tensorflow import keras
import numpy as np

from machq.types import ErrorModel
from machq.codes import RotatedPlanarCode
from machq.noise import CircuitLevelNoise
from machq.decoders import PyMatching

distance = 3
phys = 0.01
code = RotatedPlanarCode(
    x_distance=distance, z_distance=distance, noise_profile=CircuitLevelNoise(p=phys)
)

code.logical_z_memory()

num_samples = 1e5
train_frac = 0.8

noisy_circuit = code.circuit

error_model = ErrorModel(circuit=noisy_circuit)
detectors_flipped, observables_flipped = error_model.detector_events_as_binary(
    num_shots=num_samples
)

training_detectors, training_observables = (
    detectors_flipped[0 : int(train_frac * num_samples)],
    observables_flipped[0 : int(train_frac * num_samples)],
)


testing_detectors, testing_observables = (
    detectors_flipped[int(train_frac * num_samples) : :],
    observables_flipped[int(train_frac * num_samples) : :],
)

model = keras.Sequential(
    [
        keras.layers.Flatten(training_detectors, input_shape=(24,)),
        keras.layers.Dense(
            128,
            activation="relu",
        ),
        keras.layers.Dense(1),
    ]
)

model.compile(
    optimizer="adam",
    loss=keras.losses.BinaryFocalCrossentropy(from_logits=False),
    metrics=["accuracy"],
)

model.fit(training_detectors, training_observables, epochs=10)

test_loss, test_acc = model.evaluate(testing_detectors, testing_detectors, verbose=2)

print("\nTest accuracy:", test_acc)
