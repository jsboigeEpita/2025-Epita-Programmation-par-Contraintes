from visualization import animate_orbit

'''
MU: standard gravitational parameter (here earth)
A:  average distance from the center of the planet (here earth) to satellite
E: aka eccentricity, shape of the orbit. 0 = perfect circle
I:  aka inclination, how tilted the satellite's orbit is relative to Earth's equator (could change to add more satelite)
OMEGA: jsp ce que ca represent hassoul but in degrees 'direction to the ascending node'
W: The angle that tells us where the satellite is closest to Earth in its orbit.
R: earth radius
NUM_FRAMES: number of frames for the visualisations
'''

# Parameters for three satellites
MU = 398600.4418
A = [7000, 7500, 8000]
EC = [0.01, 0.02, 0.03]
IC = [45, 50, 55]
OMEGA = [60, 125, 200]
W = [30, 35, 40]
R = 6371
NUM_FRAMES = 1000
LABELS = [
    "Tokyo", "New York", "London", "Paris", "Berlin",
    "Sydney", "Rome", "Madrid", "Toronto", "Mexico City",
    "Rio de Janeiro", "Cape Town", "Mumbai", "Bangkok", "Seoul",
    "Dubai", "Istanbul", "Moscow", "Beijing", "Shanghai",
    "Singapore", "Hong Kong", "Amsterdam", "Vienna", "Buenos Aires",
    "Cairo", "Johannesburg", "Lisbon", "Stockholm", "Helsinki"
]


animate_orbit(speed=50, number_of_satellites=2, number_of_tasks=30, labels=LABELS, MU=MU, A=A, EC=EC, IC=IC, OMEGA=OMEGA, W=W, R=R, NUM_FRAMES=NUM_FRAMES)
