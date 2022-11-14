from typing import List, Tuple
import itertools
from abc import ABC, abstractmethod

from machq.types import Circuit, Qubit
from machq.noise import NoiseProfile, DepolarizingNoise, NoiseChannels


class QuantumErrorCorrectionCode(ABC):
    "An abstract base class for quantum error correction codes."

    name = "QEC_Code"

    def __init__(self, x_distance: int, z_distance: int, noise_profile: NoiseProfile):
        self.x_distance = x_distance
        self.z_distance = z_distance

        self.x_dim = None
        self.z_dim = None

        self.qubit_coords = None

        self.noise_profile = noise_profile
        self.circuit = Circuit(noise_profile=self.noise_profile)

    def __str__(self) -> str:
        return f"{self.name}_{self.x_distance}x{self.z_distance}"

    def clean_circuit(self):
        """A function to remove all entries from the circuit, except the qubit identifiers"""
        self.circuit.clear
        self.circuit.add_qubits(qubit_coords=self.qubit_coords)

    @abstractmethod
    def define_data(self):
        """A method for getting the coordinates of data qubits, varies between codes."""

    @abstractmethod
    def define_auxiliary(self):
        """A method for getting the coordinates of auxiliary qubits, varies between codes."""

    @abstractmethod
    def _measure_syndromes_(self):
        """A function describing how syndromes are measured in the code; varies between codes."""

    @abstractmethod
    def logical_x_memory(self, rounds: int = None):
        """A function describing how to encode and maintain a logical plus state"""

    @abstractmethod
    def logical_z_memory(self, rounds: int = None):
        """A function describing how to encode and maintain a logical zero state"""

    def time_step(self):
        """Add a time step to the circuit."""
        self.circuit.time_step(idle_noise=self.noise_profile.idle_noise)
