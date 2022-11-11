import pymatching
import sinter
import stim

import numpy as np


def logical_failure_probability(circuit: stim.Circuit, num_shots: int) -> int:
    num_detectors = circuit.num_detectors
    num_observables = circuit.num_observables

    # Sample the circuit.
    sampler = circuit.compile_detector_sampler()
    detection_events, observable_flips = sampler.sample(
        int(num_shots), separate_observables=True
    )

    # Extract decoder configuration data from the circuit.
    detector_error_model = circuit.detector_error_model(
        decompose_errors=True, approximate_disjoint_errors=True
    )

    # Run the decoder.
    predictions = sinter.predict_observables(
        dem=detector_error_model,
        dets=detection_events,
        decoder="pymatching",
    )

    # Count the mistakes.
    num_errors = 0
    for actual_flip, predicted_flip in zip(observable_flips, predictions):
        if not np.array_equal(actual_flip, predicted_flip):
            num_errors += 1
    return num_errors / int(num_shots)
