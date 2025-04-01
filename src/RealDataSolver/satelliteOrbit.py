import numpy as np

def satellite_position(t, MU, A, EC, IC, OMEGA, W):
    """
    Position of the satellite at a time t
    """
    i = np.radians(IC)
    omega = np.radians(OMEGA)
    w = np.radians(W)

    # how fast the satellite orbits Earth
    n = np.sqrt(MU / (A ** 3))

    # approximate position in orbit
    M = n * t

    # i have no clue what i do here but Kepler's equation
    E = M
    for _ in range(5):
        E = M + EC * np.sin(E)
    nu = 2 * np.arctan2(np.sqrt(1 + EC) * np.sin(E / 2), np.sqrt(1 - EC) * np.cos(E / 2))
    # distance from the center of the Earth to the satellite
    r = (A * (1 - EC ** 2)) / (1 + EC * np.cos(nu))
    x_p = r * np.cos(nu)
    y_p = r * np.sin(nu)

    # calculate the values for the rotation of the orbit
    cos_w, sin_w = np.cos(w), np.sin(w)
    cos_i, sin_i = np.cos(i), np.sin(i)
    cos_omega, sin_omega = np.cos(omega), np.sin(omega)

    # turn into 3D
    x = (cos_omega * cos_w - sin_omega * sin_w * cos_i) * x_p + (-cos_omega * sin_w - sin_omega * cos_w * cos_i) * y_p
    y = (sin_omega * cos_w + cos_omega * sin_w * cos_i) * x_p + (-sin_omega * sin_w + cos_omega * cos_w * cos_i) * y_p
    z = (sin_w * sin_i) * x_p + (cos_w * sin_i) * y_p

    return x, y, z, r
