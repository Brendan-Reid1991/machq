from __future__ import annotations
from typing import List, Tuple, Optional, NamedTuple, NewType
import stim

Distance = NewType("Distance", int)


class Qubit(NamedTuple):
    """A class that allows easy reference to
    qubit coordinates.
    """

    x: int
    y: int

    def __add__(self, other):
        if isinstance(other, tuple) or isinstance(other, list):
            other = Qubit(*other)
        if isinstance(other, Qubit):
            return Qubit(self.x + other.x, self.y + other.y)
        raise NotImplementedError()

    def __sub__(self, other):
        if isinstance(other, tuple) or isinstance(other, list):
            other = Qubit(*other)
        if isinstance(other, Qubit):
            return Qubit(self.x - other.x, self.y - other.y)
        raise NotImplementedError()

    def __mul__(self, other):
        if isinstance(other, int):
            return Qubit(self.x * other, self.y * other)
        raise NotImplementedError()

    def __eq__(self, other):
        if isinstance(other, Qubit):
            return self.x == other.x and self.y == other.y
