import numpy as np
from scipy.integrate import ode
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class OrbitPropagator:
    def __init__(self, r0, v0, tspan, dt, central_body):
        # initial state of the satellite
        self.r0 = r0
        self.v0 = v0

        # total period/timespan of the orbit
        self.tspan = tspan
        # time interval for which successive position and velocity is calculated
        self.dt = dt
        # Total number of time steps
        self.steps = int(np.ceil(self.tspan/self.dt))

        # dictionary containing the properties of the central body
        self.central_body = central_body

        # an empty matrix initialized to store the state of the satellite, position & velocity
        # for each time step taken
        self.ys = np.zeros((self.steps, 6))
        # a column vector for all the timesteps
        self.ts = np.zeros((self.steps, 1))

        # initial conditions and insert into ys as state for the first state
        self.y0 = self.r0 + self.v0
        self.ys[0] = np.array(self.y0)
        self.step_count = 1

        self.solver = ode(self.diff_y)
        self.solver.set_integrator('lsoda')
        self.solver.set_initial_value(self.y0, 0)  # initial state & time

    def propagate(self):
        # loop to propagate through the orbit step by step
        while self.solver.successful() and self.step_count < self.steps:
            self.solver.integrate(self.solver.t + self.dt)
            self.ts[self.step_count] = self.solver.t
            self.ys[self.step_count] = self.solver.y
            self.step_count = self.step_count + 1

        # get position for all the steps in orbit so that it can be plotted
        self.rs = self.ys[:, :3]
        self.vs = self.ys[:, 3:]


    # function to numerically calculate the derivatives of the state of the object
    # which consists of position vector and velocity vector
    # Those derivative values are passed to the ode solver of scipy module which integrate
    # the velocity to calculate the position and integrate the accl. to get velocity


    def diff_y(self, t, y):
        rx, ry, rz, vx, vy, vz = y

        # position vector
        r = np.array([rx, ry, rz])

        # magnitude of r also known as the norm of vector r
        mag_r = np.linalg.norm(r)

        # acceleration of the body calculated using newton's law of gravitation
        ax, ay, az = -(r * self.central_body.mu) / mag_r ** 3

        # we return the derivative of position(velocity) and derivative of velocity(acceleration)
        return [vx, vy, vz, ax, ay, az]

    def plot_3d(self, center_coords, show=False, save=False):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # plot trajectory
        ax.plot(self.rs[:, 0], self.rs[:, 1], self.rs[:, 2], 'k', label="Trajectory")
        ax.plot([self.rs[0, 0]], [self.rs[0, 1]], [self.rs[0, 2]], 'ko', label="Inital Position")

        ax.plot_surface(center_coords[0], center_coords[1], center_coords[2], cmap="Blues", alpha=0.6)

        plt.show()
        plt.savefig("Plot.png", dpi=300)

