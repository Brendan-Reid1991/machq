from machq.noise import DepolarizingNoise
from machq.codes import RotatedPlanarCodeFlags

if __name__ == "__main__":
    code = RotatedPlanarCodeFlags(noise_profile=DepolarizingNoise(p=0.001))
    print(code.auxiliary_qubits)
    print(code.flag_qubits)
