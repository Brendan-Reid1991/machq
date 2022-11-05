#### This code taken from the stim 'Getting Started' notebook
#### https://github.com/quantumlib/Stim/blob/main/doc/getting_started.ipynb


import numpy as np

import stim

from machq.pymatching_glue_code import (
    predict_observable_errors_using_pymatching,
)


def get_logical_errors(
    data_circuit: stim.Circuit,
    num_shots: int = 1000,
) -> float:
    """
    Simulate the data_circuit num_shots times, attempt to decode using pymatching
    and count the number of logical errors. If supplied, the decoding will be done
    using the decoding_circuit graph.

    Parameters
    ----------
    data_circuit : stim.Circuit
        Circuit to be simulated in order to obtain data.
    decoding_circuit : stim.Circuit
        Circuit to be used to generate the decoding graph. If not supplied, the
        data circuit will be used instead.
    num_shots : int
        Number of times to simulate the data_circuit.

    Returns
    -------
    int
        Number of logical errors that occur in num_shots runs of the circuit.
    """
    # get number of detectors
    num_data_detectors = data_circuit.num_detectors

    # generate samples from the data circuit
    shots = data_circuit.compile_detector_sampler().sample(
        int(num_shots), append_observables=True
    )

    detector_parts = shots[:, :num_data_detectors]
    actual_observable_parts = shots[:, num_data_detectors:]

    predicted_observable_parts = predict_observable_errors_using_pymatching(
        data_circuit, detector_parts
    )
    num_errors = 0
    for actual, predicted in zip(actual_observable_parts, predicted_observable_parts):
        if not np.array_equal(actual, predicted):
            num_errors += 1

    return num_errors / num_shots
