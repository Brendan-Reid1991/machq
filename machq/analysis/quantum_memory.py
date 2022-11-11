from machq.codes import QuantumErrorCorrectionCode


class QuantumMemory:
    """A class that allows you to run quantum memory experiments."""

    def __init__(self, code: QuantumErrorCorrectionCode, decoder):
        self.code = code

    def memory_experiment(self, logical: str):
        """Run a quantum memory experiment.

        Parameters
        ----------
        logical : str
            What kind of logical you want to maintain in memory.
            Must of one of X or Z
        """
        if logical.casefold() not in ["x", "z"]:
            raise ValueError(
                "Can only run quantum memory experiments on logical X or Z states"
            )
