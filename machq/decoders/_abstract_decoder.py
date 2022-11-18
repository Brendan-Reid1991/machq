from abc import ABC, abstractmethod

from machq.types import Circuit


class Decoder(ABC):
    """An abstract class for decoders."""

    name = "Decoder"

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.stim_circuit = circuit.as_stim

    def __str__(self) -> str:
        return f"{self.name}"

    @abstractmethod
    def logical_failure_probability(num_shots: int) -> float:
        """A function for returning the logical failure probability, given the number of shots to sample the DEM over.

        Parameters
        ----------
        num_shots : int
           Number of shots to sample over.

        Returns
        -------
        float
            The probability of a logical failure in the circuit
        """
