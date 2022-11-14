from __future__ import annotations

from typing import List, Dict, Tuple, NamedTuple, Type
import numpy as np
from numpy import ndarray, int64, float64
import os
import pandas as pd

from machq.types import Distance
from machq.codes import QuantumErrorCorrectionCode
from machq.decoders import Decoder
from machq.noise import NoiseProfile
from machq.analysis import QuantumMemory


class ExperimentPair(NamedTuple):
    code: Type[QuantumErrorCorrectionCode]
    decoder: Type[Decoder]


class CodeExperiment:
    """A class that allows multiple experiments to be run on a code."""

    def __init__(
        self,
        code: Type[QuantumErrorCorrectionCode],
        decoder: Type[Decoder],
        noise_profile: NoiseProfile,
        distances: List[Distance],
        physical_errors: List[float] | ndarray[np.float],
        qec_rounds: int = None,
    ):
        self._code = code
        self._decoder = decoder
        self._noise_profile = noise_profile

        self.distances = sorted(distances)
        self.physical_errors = sorted(physical_errors)
        self.qec_rounds = qec_rounds

        self.experiment_name = (
            f"{self._code.name}_{self._noise_profile.name}_{self._decoder.name}"
        )

    def _qmem_object(
        self, x_dist: Distance, z_dist: Distance, noise_profile: NoiseProfile
    ) -> QuantumMemory:
        """_summary_

        Parameters
        ----------
        x_dist : _type_
            _description_
        z_dist : _type_
            _description_
        noise_profile : _type_
            _description_
        """
        # TODO Make more general here, some codes will only take a single distance parameter rather than both x and z.

        code = self._code(
            x_distance=x_dist, z_distance=z_dist, noise_profile=noise_profile
        )
        return QuantumMemory(code=code, decoder=self._decoder)

    def collection(self) -> Dict[Tuple[int, float], QuantumMemory]:
        """Return a collection of QuantumMemory objects as a dict."""
        return {
            (dist, phys): self._qmem_object(dist, dist, self._noise_profile(p=phys))
            for dist in self.distances
            for phys in self.physical_errors
        }

    def _create_csv_(self):
        """Create a CSV file pertaining to this CodeExperiment."""

        csv_dtypes = {
            "Code": str,
            "NoiseProfile": str,
            "Decoder": str,
            "Pauli": str,
            "X-Distance": int64,
            "Z-Distance": int64,
            "Num_Rounds": int64,
            "Num_Shots": int64,
            "Physical Error": float64,
            "Logical Error Mean": float64,
            "Logical Error Std": float64,
        }

        data_filepath = os.getcwd() + f"experiments/data/"
        plot_filepath = (
            os.getcwd()
            + f"experiments/plots/{self._code.name}_{self._noise_profile.name}_{self._decoder.name}/"
        )

        for path in [data_filepath, plot_filepath]:
            if not os.path.exists(path=path):
                os.makedirs(name=path)

        csv_headers = list(csv_dtypes.keys())
        csv_path = data_filepath + f"{self.experiment_name}.csv"
        if not os.path.exists(csv_path):
            dataframe = pd.DataFrame(data=[], columns=csv_headers)
            dataframe.astype(dtype=csv_dtypes)
            dataframe.to_csv(csv_path, index=False)


if __name__ == "__main__":
    import numpy as np

    from machq.codes import RotatedPlanarCode
    from machq.decoders import PyMatching
    from machq.noise import DepolarizingNoise

    distances = [3, 5, 7, 9]
    physical_errors = np.logspace(-5, -2, 10)
    experiment = CodeExperiment(
        code=RotatedPlanarCode,
        decoder=PyMatching,
        noise_profile=DepolarizingNoise,
        distances=distances,
        physical_errors=physical_errors,
    )

    experiment._create_csv_()
