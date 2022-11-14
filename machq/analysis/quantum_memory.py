from machq.codes import QuantumErrorCorrectionCode
from machq.decoders import Decoder


class QuantumMemory:
    """A class that allows you to run quantum memory experiments."""

    def __init__(self, code: QuantumErrorCorrectionCode, decoder: Decoder):
        self.code = code
        self.decoder = decoder(circuit=self.code.circuit)

    def memory_experiment(self, logical: str, rounds: int = None, num_shots: int = 1e4):
        """Run a quantum memory experiment.

        Parameters
        ----------
        logical : str
            What kind of logical you want to maintain in memory.
            Must of one of X or Z
        rounds : int
            How many rounds of syndrome extraction to perform, default None.
            Runs a number of rounds equal to the weight of the logical operator if None.
        num_shots : int
            How many shots to sample over, by default 1e4.
        """
        if logical.casefold() not in ["x", "z"]:
            raise ValueError(
                "Can only run quantum memory experiments on logical X or Z states"
            )

        self.code.clean_circuit()
        if logical.casefold() == "x":
            rounds = rounds if rounds is not None else self.code.x_distance
            self.code.logical_x_memory(rounds=rounds)

        if logical.casefold() == "z":
            rounds = rounds if rounds is not None else self.code.z_distance
            self.code.logical_z_memory(rounds=rounds)

        return self.decoder.logical_failure_probability(num_shots=num_shots)
