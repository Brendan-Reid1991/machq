from typing import Tuple
import stim
import numpy as np
from numpy.typing import NDArray

from machq.types._circuit_ import Circuit


class ErrorModel:
    """This class enables extraction of the detector error models
    from stim Circuits, and allows sampling from them in order to
    generate syndromes.

    Parameters
    ----------
    circuit : Circuit
        The circuit to consider.

    """

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.stim_circuit = circuit.as_stim

    def detector_error_model(self, graphlike: bool = True):
        """Return the detector error model (dem) of the circuit.

        Parameters
        ----------
        graphlike : bool, optional
            Whether or not to return a graphlike dem, by default True.
            If False, a hypergraph dem will be returned.

        Returns
        -------
        stim.DetectorErrorModel
        """
        if graphlike:
            return self.stim_circuit.detector_error_model(
                approximate_disjoint_errors=True, decompose_errors=True
            )
        return self.stim_circuit.detector_error_model(approximate_disjoint_errors=True)

    def detector_sampler(self):
        """Return a detector sampler object

        Returns
        -------
        stim.CompiledDetectorSampler
        """
        return self.stim_circuit.compile_detector_sampler()

    def detector_events(
        self, num_shots: int = 1e4
    ) -> Tuple[NDArray[bool], NDArray[bool]]:
        """Get the detection events and corresponding observable flips.

        Returns
        -------
        Tuple[NDArray[bool], NDArray[bool]]
            Return a tuple, whose elements are a Numpy array of detection events of shape (num_shots * num_detectors) and an array of observable flips
            of shape (num_shots * 1). The boolean entries refer to if a detector (respectively observable) was flipped.
        """

        return self.detector_sampler().sample(
            shots=int(num_shots), separate_observables=True
        )

    def detector_events_as_binary(
        self, num_shots: int = 1e4
    ) -> Tuple[NDArray[int], NDArray[int]]:
        """Get the detection events and corresponding observable flips.

        Returns
        -------
        Tuple[NDArray[bool], NDArray[bool]]
            Return a tuple, whose elements are a Numpy array of detection events of shape (num_shots * num_detectors) and an array of observable flips
            of shape (num_shots * 1). The boolean entries refer to if a detector (respectively observable) was flipped.
        """

        events, observables = self.detector_sampler().sample(
            shots=int(num_shots), separate_observables=True
        )
        return np.array(events, dtype=int), np.array(observables, dtype=int)

    def _detectors_triggered(self, events: NDArray[bool]):
        """Observe which detectors were triggered.

        Parameters
        ----------
        events : NDArray[bool]
            A numpy array of booleans, indices of which correspond to the detectors.
        """
        if len(events) != self.stim_circuit.num_detectors:
            raise ValueError(
                "Length of detector events is not equal to the number of detectors present."
            )
        return [f"D{idx}" for idx, element in enumerate(events) if element]

    def _potential_error_patterns(self, events: NDArray[bool]):
        """Return potential error patterns from the dem file
        given a list of detector events.

        Parameters
        ----------
        events : NDArray[bool]
            A numpy array of booleans, indices of which correspond to the detectors.
        """
        potential_error_patterns = []
        for dem_entry in self.detector_error_model():
            if dem_entry.type != "error":
                continue
            probability = dem_entry.args_copy()
            probability = probability[0] if len(probability) == 1 else probability
            det_targets = [
                x.val for x in dem_entry.targets_copy() if x.is_relative_detector_id()
            ]

            if any(events[index] for index in det_targets):
                output_str = ""
                for entry in dem_entry.targets_copy():
                    if entry.is_relative_detector_id():
                        output_str += f"D{entry.val} "
                    if entry.is_separator():
                        output_str += "^ "
                    if entry.is_logical_observable_id():
                        output_str += f"L{entry.val} "
                potential_error_patterns.append((probability, output_str[0:-1]))

        return potential_error_patterns
