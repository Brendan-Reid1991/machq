from __future__ import annotations

from typing import List, Dict, Tuple, NamedTuple, Type
import numpy as np
from numpy import ndarray, int64, float64
import os
import pandas as pd
import multiprocessing as mp

from machq.types import Distance
from machq.codes import QuantumErrorCorrectionCode
from machq.decoders import Decoder
from machq.noise import NoiseProfile
from machq.analysis import QuantumMemory


class CodeExperiment:
    """A class that allows multiple experiments to be run on a code."""

    def __init__(
        self,
        code: Type[QuantumErrorCorrectionCode],
        decoder: Type[Decoder],
        noise_profile: Type[NoiseProfile],
        distances: List[Distance],
        physical_errors: List[float] | ndarray[np.float],
        qec_rounds: int = None,
        name: str = "default",
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
        self.name = name

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

    def _get_csv_data_(self) -> Tuple[str, Dict[str, object]]:
        """Return the CSV filepath and the CSV dtypes"""

        csv_filepath = (
            os.getcwd()
            + f"/experiments/{self._code.name}_{self._noise_profile.name}_{self._decoder.name}/"
        )

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

        return csv_filepath, csv_dtypes

    def _create_csv_(self):
        """Create a CSV file pertaining to this CodeExperiment."""

        filepath, csv_dtypes = self._get_csv_data_()
        data_filepath = filepath + "/data/"
        plot_filepath = filepath + "/plot/"
        for path in [data_filepath, plot_filepath]:
            if not os.path.exists(path=path):
                os.makedirs(name=path)

        csv_headers = list(csv_dtypes.keys())
        csv_path = data_filepath + f"{self.name}.csv"
        if not os.path.exists(csv_path):
            dataframe = pd.DataFrame(data=[], columns=csv_headers)
            dataframe.astype(dtype=csv_dtypes)
            dataframe.to_csv(csv_path, index=False)

    def open_csv(self) -> pd.DataFrame:
        """Open the current CSV

        Returns
        -------
        pandas.DataFrame
            The CSV as pandas.DataFrame type.
        """
        filepath, csv_dtypes = self._get_csv_data_()
        return pd.read_csv(filepath + f"/data/{self.name}.csv", dtype=csv_dtypes)

    def _update_csv_(
        self,
        pauli: str,
        distance: int,
        num_rounds: int,
        num_shots: int,
        physical_error: float,
        logical_error_mean: float,
        logical_error_std: float,
    ):
        """Update the existing CSV file with new data.

        Parameters
        ----------
        pauli : str
            The logical Pauli experiment.
        distance : int
            The code distance to take, assumes X==Z distance.
        num_rounds : int
            How many rounds of error correction to perform.
        num_shots : int
            How mnay shots the data was sampled over
        physical_error : float
            The physical error rate to take; this determines the
            number of shots to sample from.
        logical_error_mean : float
            The mean value of the output logical error.
        logical_error_std : float
            The standard deviation of the output logical error.

        """
        filepath, csv_dtypes = self._get_csv_data_()
        new_df = pd.DataFrame(
            data=[
                [
                    self._code.name,
                    self._noise_profile.name,
                    self._decoder.name,
                    pauli,
                    distance,
                    distance,
                    num_rounds,
                    num_shots,
                    physical_error,
                    logical_error_mean,
                    logical_error_std,
                ]
            ],
            columns=list(csv_dtypes.keys()),
        )

        current_df = self.open_csv()
        temp = pd.concat([current_df, new_df], axis=0)
        temp.astype(dtype=csv_dtypes)
        temp.to_csv(filepath, index=False)

    def _get_data_(
        self,
        pauli: str,
        distance: int,
        num_rounds: int,
        physical_error: float,
        processes: int = 1,
    ):
        """Run an instance of the code class through the decoder, and store the data to the
        relevant CSV

        Parameters
        ----------
        pauli : str
            The logical memory experiment to run.
        distance : int
            The code distance to take, assumes X==Z distance.
        num_rounds : int
            How many rounds of error correction to perform.
        physical_error : float
            The physical error rate to take; this determines the
            number of shots to sample from.
        processes : int
            How many logical CPUs to parallelise the result over,
            by default 1.
        """

        num_shots = max(1, min(2 * (physical_error**-2), 1e7) // processes)

        qmem = self.collection()[(distance, physical_error)]

        if processes > 1:
            pool = mp.Pool(processes=processes)
            args = [[pauli, num_rounds, num_shots]] * processes
            result = pool.starmap(qmem.memory_experiment, args)
        else:
            result = qmem.memory_experiment(
                logical=pauli, rounds=num_rounds, num_shots=num_shots
            )

        if isinstance(result, list):
            mean = np.mean(result)
            std = np.std(result)
        else:
            mean = result
            std = 0

        self._update_csv_(
            pauli=pauli,
            distance=distance,
            num_rounds=num_rounds,
            num_shots=int(num_shots * processes),
            physical_error=physical_error,
            logical_error_mean=mean,
            logical_error_std=std,
        )


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
    experiment._get_data_(pauli="Z", distance=3, num_rounds=3, physical_error=0.01)
