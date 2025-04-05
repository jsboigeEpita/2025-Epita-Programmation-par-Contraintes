import numpy as np

class Satellite:
    def __init__(self, MU, A, EC, IC, OMEGA, W):
        self.MU = MU
        self.A = A
        self.EC = EC
        self.IC = np.radians(IC)
        self.OMEGA = np.radians(OMEGA)
        self.W = np.radians(W)

    def position_at(self, t):
        """
        Calculate the position of the satellite at a given time t.
        """
        # How fast the satellite orbits Earth
        n = np.sqrt(self.MU / (self.A ** 3))

        # Approximate position in orbit
        M = n * t

        # Solve Kepler's equation
        E = M
        for _ in range(5):
            E = M + self.EC * np.sin(E)

        nu = 2 * np.arctan2(np.sqrt(1 + self.EC) * np.sin(E / 2), np.sqrt(1 - self.EC) * np.cos(E / 2))

        # Distance from the center of the Earth to the satellite
        r = (self.A * (1 - self.EC ** 2)) / (1 + self.EC * np.cos(nu))
        x_p = r * np.cos(nu)
        y_p = r * np.sin(nu)

        # Calculate the values for the rotation of the orbit
        cos_w, sin_w = np.cos(self.W), np.sin(self.W)
        cos_i, sin_i = np.cos(self.IC), np.sin(self.IC)
        cos_omega, sin_omega = np.cos(self.OMEGA), np.sin(self.OMEGA)

        # Turn into 3D
        x = (cos_omega * cos_w - sin_omega * sin_w * cos_i) * x_p + (-cos_omega * sin_w - sin_omega * cos_w * cos_i) * y_p
        y = (sin_omega * cos_w + cos_omega * sin_w * cos_i) * x_p + (-sin_omega * sin_w + cos_omega * cos_w * cos_i) * y_p
        z = (sin_w * sin_i) * x_p + (cos_w * sin_i) * y_p

        return x, y, z, r