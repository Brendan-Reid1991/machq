import pytest

from machq.noise import NoiseChannels


class TestNoiseChannels:
    @pytest.mark.parametrize("p", [0.1, 0.5, 0.2])
    def test_depolarize_1(self, p):
        assert NoiseChannels.Depolarize1(p=p) == (p / 3,) * 3

    @pytest.mark.parametrize("p", [0.1, 0.5, 0.2])
    def test_depolarize_2(self, p):
        assert NoiseChannels.Depolarize2(p=p) == (p / 15,) * 15

    @pytest.mark.parametrize("p", [0.1, 0.5, 0.2])
    def test_x_error(self, p):
        assert NoiseChannels.XError(p=p) == (p, 0, 0)

    @pytest.mark.parametrize("p", [0.1, 0.5, 0.2])
    def test_y_error(self, p):
        assert NoiseChannels.YError(p=p) == (0, p, 0)

    @pytest.mark.parametrize("p", [0.1, 0.5, 0.2])
    def test_z_error(self, p):
        assert NoiseChannels.ZError(p=p) == (0, 0, p)
