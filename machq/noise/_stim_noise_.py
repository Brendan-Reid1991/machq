from typing import Tuple
import stim


class NoiseChannels:
    """A class that collects all stim noise channels.
    Each channel is a static method, and
    takes as input a depolarizing
    parameter and returns a Tuple.
    """

    @staticmethod
    def Depolarize1(p: float) -> Tuple:
        """Unbiased, single qubit depolarizing noise of strength p"""
        return (p / 3,) * 3

    @staticmethod
    def Depolarize2(p: float) -> Tuple:
        """Unbiased, two qubit depolarizing noise of strength p"""
        return (p / 15,) * 15

    @staticmethod
    def XError(p: float) -> Tuple:
        """X-Error of strength p"""
        return (p, 0, 0)

    @staticmethod
    def YError(p: float) -> Tuple:
        """Y-Error of strength p"""
        return (0, p, 0)

    @staticmethod
    def ZError(p: float) -> Tuple:
        """Z-Error of strength p"""
        return (0, 0, p)
