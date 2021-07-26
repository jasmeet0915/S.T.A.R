import os
import numpy as np
from scipy.integrate import ode
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from data.planetary_data import earth
from OrbitPropagator import OrbitPropagator as op
from central_body import CentralBody
from satellite import Satellite
import particlecache
import utils
plt.style.use('dark_background')
import pandas as pd


def init_central_body():
    cb = CentralBody("Earth", earth['mass'], earth['radius'], axis_tilt=23.5)
    return cb


cb = init_central_body()


def get_orbital_elements(sat_name="iss"):
    a = cb.radius + (iss['perigee height'] + iss['apogee height'])/2
    eles = [a, iss['e'], iss['i'], iss['raan'], iss['arg_perigee'], iss['ma@epoch'], iss['Epoch']]
    period = (24.0*3600.0)/iss['revs/day']
    return eles, period


def get_tle_data(path):
    with open(path, 'r') as f:
        tle_data = f.readlines()

    tle_data = [tle_data[i:i+3] for i in range(0, len(tle_data), 3)]
    return tle_data


''' 
Blender simulation data
'''
# fps of simulation
sim_fps = 24

# period of earth rotation in sim in seconds
sim_earth_period = 120.0

# real time to sim time conversion factor
real2sim = sim_earth_period/(24.0 * 3600.0)


if __name__ == "__main__":
    cb = init_central_body()
    sphere_coords = cb.plot_attributes()
    tle_data = get_tle_data("data/starlink.txt")

    count = 1

    for tle in tle_data:
        print("....Calculating State Vectors for Starlink No. " + str(count) + "....")
        # create satellite object and propagate it using orbital elements
        sat1 = Satellite(sat_id=1, name="ISS", center_body=cb, sat_type="Communication")
        sat1r0, sat1v0 = sat1.propagate_with_tle(tle)

        # calculates real time dt for sim time dt of each frame
        dt = 1/sim_fps * 1/real2sim 

        sat1r0 = sat1r0.tolist()
        sat1v0 = sat1v0.tolist()
        propagtor1 = op(sat1r0, sat1v0, sat1.period, dt=dt, central_body=cb)
        propagtor1.propagate()
        propagtor1.rs = propagtor1.rs * 1/6378
        if count == 1:
            coords = propagtor1.rs
        else:
            coords = np.concatenate((coords, propagtor1.rs), axis=1)
        count= count + 1

print(" ")
print("....Creating final_coords list for writing location data to Blender's Particle Cache....")

final_coords = []

for k in range(coords.shape[0]):
    a = coords[k].tolist()
    t = [a[i:i+3] for i in range(0, len(a), 3)]
    final_coords.append(t)

for e in range(len(final_coords)):
    for c in range(len(final_coords[e])):
        final_coords[e][c] = tuple(final_coords[e][c])



currentDirectory = os.getcwd()
particleCachePath = os.path.normpath(currentDirectory + os.sep + os.pardir)+"/blendcache_earth1."


cache = particlecache.PointCache(particleCachePath, 0)


final_coords = final_coords * 15


count1 = 0
for frame in cache.files:
    print("....Writing in Location Data in" + str(frame[1]) + "file for frame no. " + str(frame[0]) + "....")
    particle_frame = particlecache.CacheFrame(frame[1])
    particle_frame.read(particleCachePath, True)
    locdata = particle_frame.get_data('LOCATION')
    particle_frame.set_data('LOCATION', final_coords[count1]) #at this point it's only in python
    particle_frame.write(particleCachePath)
    print(" ")
    count1 = count1 + 1



