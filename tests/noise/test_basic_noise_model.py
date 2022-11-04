import pytest

from machq.noise import DepolarizingNoise, CircuitLevelNoise, NoiseChannels

prob = 0.1


class TestDepolarizingNoise:
    @pytest.mark.parametrize("p", [-0.1, 1.5])
    def test_check_validity(self, p):
        with pytest.raises(ValueError, match=r".*Invalid noise parameter*"):
            DepolarizingNoise(p=p)

    @pytest.fixture(scope="function")
    def depolarize_noise(self):
        return DepolarizingNoise(p=prob)

    def test_single_qubit_gate_noise(self, depolarize_noise):
        assert depolarize_noise.single_qubit_gate_noise == NoiseChannels.Depolarize1(
            p=prob
        )

    def test_two_qubit_gate_noise(self, depolarize_noise):
        assert depolarize_noise.two_qubit_gate_noise == NoiseChannels.Depolarize2(
            p=prob
        )

    def test_measurement_flip_prob(self, depolarize_noise):
        assert depolarize_noise.measurement_flip_prob == prob

    def test_reset_noise(self, depolarize_noise):
        assert depolarize_noise.reset_noise == NoiseChannels.Depolarize1(p=prob)

    def test_idle_noise(self, depolarize_noise):
        assert depolarize_noise.idle_noise == NoiseChannels.Depolarize1(p=prob)


class TestCircuitLevelNoise:
    @pytest.fixture(scope="function")
    def circuit_level_noise(self):
        return CircuitLevelNoise(p=prob)

    def test_single_qubit_gate_noise(self, circuit_level_noise):
        assert circuit_level_noise.single_qubit_gate_noise == NoiseChannels.Depolarize1(
            p=prob / 10
        )

    def test_two_qubit_gate_noise(self, circuit_level_noise):
        assert circuit_level_noise.two_qubit_gate_noise == NoiseChannels.Depolarize2(
            p=prob
        )

    def test_measurement_flip_prob(self, circuit_level_noise):
        assert circuit_level_noise.measurement_flip_prob == prob / 10

    def test_reset_noise(self, circuit_level_noise):
        assert circuit_level_noise.reset_noise == NoiseChannels.Depolarize1(p=prob / 10)

    def test_idle_noise(self, circuit_level_noise):
        assert circuit_level_noise.idle_noise == NoiseChannels.Depolarize1(p=prob / 10)
