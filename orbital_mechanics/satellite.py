import numpy as np
import math as m
import utils

# conversion factor for degree to radian conversion
degree2rad = np.pi/180.0


class Satellite:
    def __init__(self, sat_id, name, center_body, sat_type):
        self.sat_id = sat_id
        self.name = name
        self.sat_type = sat_type
        self.center_body = center_body

    def propagate_with_coes(self, orbital_elements):
        self.orbital_elements = orbital_elements
        a, e, i, raan, arg_periapsis, mean_anomaly, epoch = self.orbital_elements
        i = i * degree2rad
        arg_periapsis = arg_periapsis * degree2rad
        mean_anomaly = mean_anomaly * degree2rad
        raan = raan * degree2rad

        # eccentricity anomaly at epoch calculated using mean anomaly at epoch
        ea = utils.eccentric_anomaly(mean_anomaly, e)
        # true anomaly of at epoch used to calculate initial state vectors
        ta = utils.true_anomaly(ea, e)

        r_norm = a * (1-e**2)/(1+e*np.cos(ta))

        r_perif = r_norm * np.array([m.cos(ta), m.sin(ta), 0])
        v_perif = m.sqrt(self.center_body.mu*a)/r_norm * np.array([-m.sin(ea), m.cos(ea)*m.sqrt(1-e**2), 0])

        perif2eci = np.transpose(utils.eci2perif(raan, arg_periapsis, i))

        r0 = np.dot(perif2eci, r_perif)
        v0 = np.dot(perif2eci, v_perif)

        return r0, v0


    """Use this function if you want to use satellite TLE data to plot the orbit
    path: path to the file containing the TLE data"""
    def propagate_with_tle(self, tle):
        # name of satellite
        line0 = tle[0].strip()
        # TLE data
        line1 = tle[1].strip().split()
        line2 = tle[2].strip().split()

        # to do: change the check as person may not enter exactly same name as the one in tle
        # this is a condition that checks to see if the correct tle data is loaded
        '''if line0 != self.name:
            print("Name of satellite object does not match name on TLE!!")
'''
        epoch = line1[3]
        i = float(line2[2]) * degree2rad
        raan = float(line2[3]) * degree2rad
        e = line2[4]
        e = float('0.' + e)
        arg_periapsis = float(line2[5]) * degree2rad
        mean_anomaly = float(line2[6]) * degree2rad
        mean_motion = float(line2[7]) # revs/day

        self.period = (24*3600)/mean_motion

        a = (self.period**2 * self.center_body.mu/4.0/np.pi**2)**(1/3.0)

        # eccentricity anomaly at epoch calculated using mean anomaly at epoch
        ea = utils.eccentric_anomaly(mean_anomaly, e)
        # true anomaly of at epoch used to calculate initial state vectors
        ta = utils.true_anomaly(ea, e)

        r_norm = a * (1 - e ** 2) / (1 + e * np.cos(ta))

        r_perif = r_norm * np.array([m.cos(ta), m.sin(ta), 0])
        v_perif = m.sqrt(self.center_body.mu * a) / r_norm * np.array([-m.sin(ea), m.cos(ea) * m.sqrt(1 - e ** 2), 0])

        perif2eci = np.transpose(utils.eci2perif(raan, arg_periapsis, i))

        r0 = np.dot(perif2eci, r_perif)
        v0 = np.dot(perif2eci, v_perif)

        return r0, v0




