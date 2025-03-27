from imagingTaskGeneration import generate_random_points, are_points_on_surface
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
MU = 398600.4418
A = 7000
EC = 0.01
IC = 45
OMEGA = 60
W = 30
R = 6371
NUM_FRAMES = 1000

'''
# extra verification on the task points to make sure they are on the earth sphere
random_points = generate_random_points(15, R)
if are_points_on_surface(random_points, R):
    print("All points are on the surface of the sphere.")
else:
    print("Some points are not on the surface of the sphere.")
'''

animate_orbit(speed=50, MU=MU, A=A, EC=EC, IC=IC, OMEGA=OMEGA, W=W, R=R, NUM_FRAMES=NUM_FRAMES)
