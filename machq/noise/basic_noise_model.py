from abc import ABC

from machq.noise import NoiseChannels


class NoiseProfile(ABC):
    """An abstract base class for noise profiles."""

    def _check_valid_noise(self, p: float):
        """Private function to check if the noise
        parameter passed to each noise channel is valid.

        Parameters
        ----------
        p : float
            The noise parameter

        Raises
        -------
        ValueError
            If p < 0 or p > 1
        """
        if not 0 <= p <= 1:
            raise ValueError(f"Invalid noise parameter {p} passed. ")


class DepolarizingNoise(NoiseProfile):
    """A class to summarise a complete noise profile;
    covering single- and two-qubit gate noise,
    measurement flip probability, reset noise and idle noise.

    In this base class, everything is characterised by a single
    parameter p. This is typical in the literature, more specifically
    in the papers arxiv.org/abs/2205.09828 and arxiv.org/abs/1311.5003.

    By inheriting from this noise profile, any individual noise value
    can be overwritten.s
    """

    name = "depolarizing_noise"

    def __init__(self, p: float):

        self._check_valid_noise(p=p)

        self.noise_channels = NoiseChannels
        self.single_qubit_gate_noise = NoiseChannels.Depolarize1(p=p)
        self.two_qubit_gate_noise = NoiseChannels.Depolarize2(p=p)
        self.measurement_flip_prob = p
        self.reset_noise = p
        self.idle_noise = NoiseChannels.Depolarize1(p=p)


class CircuitLevelNoise(DepolarizingNoise):
    """A circuit level noise profile. Characterised by the fact that
    two qubit gates are typically an order of magnitude noisier than all other noise sources.
    """

    name = "circuit_level_noise"

    def __init__(self, p):
        super().__init__(p=p)
        self.single_qubit_gate_noise = NoiseChannels.Depolarize1(p=p / 10)
        self.measurement_flip_prob = p / 10
        self.reset_noise = p / 10
        self.idle_noise = NoiseChannels.Depolarize1(p=p / 10)
