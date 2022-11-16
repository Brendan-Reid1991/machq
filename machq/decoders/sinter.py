import pymatching
import sinter
import stim
import numpy as np

from machq.types import Circuit
from machq.decoders import Decoder


class PyMatching(Decoder):
    """A wrapper class for decoding with PyMatching,
    via sinter.
    """

    name = "PyMatching"

    def __init__(self, circuit: Circuit):
        super().__init__(circuit=circuit)

    def logical_failure_probability(self, num_shots: int) -> float:
        """This function taken from Gidneys "Getting Started" notebook.
        https://github.com/quantumlib/Stim/blob/main/doc/getting_started.ipynb

        Parameters
        ----------
        num_shots : int
            Number of shots to sample over.

        Returns
        -------
        float
            The probability of a logical failure in the circuit
        """
        num_detectors = self.stim_circuit.num_detectors
        num_observables = self.stim_circuit.num_observables

        # Sample the circuit.
        sampler = self.stim_circuit.compile_detector_sampler()
        detection_events, observable_flips = sampler.sample(
            int(num_shots), separate_observables=True
        )

        # Extract decoder configuration data from the circuit.
        detector_error_model = self.stim_circuit.detector_error_model(
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
