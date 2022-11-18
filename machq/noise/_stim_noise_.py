from typing import Tuple
import stim


class NoiseChannels:
    """A class that collects all stim noise channels.
    Each channel is a static method, and
    takes as input a depolarizing
    parameter and returns a Tuple.
    """

    @staticmethod
    def Depolarize1(p: float) -> Tuple[str, float]:
        """Unbiased, single qubit depolarizing noise of strength p"""
        return "DEPOLARIZE1", p

    @staticmethod
    def Depolarize2(p: float) -> Tuple[str, float]:
        """Unbiased, two qubit depolarizing noise of strength p"""
        return "DEPOLARIZE2", p

    @staticmethod
    def XError(p: float) -> Tuple[str, float]:
        """X-Error of strength p"""
        return "X_ERROR", p

    @staticmethod
    def YError(p: float) -> Tuple[str, float]:
        """Y-Error of strength p"""
        return "Y_ERROR", p

    @staticmethod
    def ZError(p: float) -> Tuple[str, float]:
        """Z-Error of strength p"""
        return "Z_ERROR", p
