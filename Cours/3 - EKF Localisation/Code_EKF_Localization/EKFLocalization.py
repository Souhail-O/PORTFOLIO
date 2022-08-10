from math import sin, cos, atan2, pi, sqrt
import matplotlib.pyplot as plt
import numpy as np
from sympy.functions.elementary.complexes import im
#from sympy import *
import sympy as sp
import autograd.numpy as np
from autograd import grad, jacobian

# ---- Helper functions ----

# Init displays
show_animation = True
f, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(14, 7))
ax3 = plt.subplot(3, 2, 2)
ax4 = plt.subplot(3, 2, 4)
ax5 = plt.subplot(3, 2, 6)


# Display error ellipses
def plot_covariance_ellipse(xEst, PEst, axes, lineType):
    """
    Plot one covariance ellipse from covariance matrix
    """

    Pxy = PEst[0:2, 0:2]
    eigval, eigvec = np.linalg.eig(Pxy)

    if eigval[0] >= eigval[1]:
        bigind = 0
        smallind = 1
    else:
        bigind = 1
        smallind = 0

    if eigval[smallind] < 0:
        print('Pb with Pxy :\n', Pxy)
        exit()

    t = np.arange(0, 2 * pi + 0.1, 0.1)
    a = sqrt(eigval[bigind])
    b = sqrt(eigval[smallind])
    x = [3 * a * cos(it) for it in t]
    y = [3 * b * sin(it) for it in t]
    angle = atan2(eigvec[bigind, 1], eigvec[bigind, 0])
    rot = np.array([[cos(angle), sin(angle)],
                    [-sin(angle), cos(angle)]])
    fx = rot @ (np.array([x, y]))
    px = np.array(fx[0, :] + xEst[0, 0]).flatten()
    py = np.array(fx[1, :] + xEst[1, 0]).flatten()
    axes.plot(px, py, lineType)


# fit angle between -pi and pi
def angle_wrap(a):
    if (a > np.pi):
        a = a - 2 * pi
    elif (a < -np.pi):
        a = a + 2 * pi
    return a


# composes two transformations
def tcomp(tab, tbc):
    assert tab.ndim == 2
    assert tbc.ndim == 2

    result = tab[2, 0] + tbc[2, 0]

    result = angle_wrap(result)
    s = sin(tab[2, 0])
    c = cos(tab[2, 0])
    tac = tab[0:2] + np.array([[c, -s], [s, c]]) @ tbc[0:2]
    tac = np.vstack((tac, result))

    return tac


# ---- Simulator functions ----

# return true control at step k
def get_robot_control(k):
    global nSteps
    # generate  sin trajectory
    u = np.array([[0, 0.025,  0.1*np.pi / 180 * sin(3*np.pi * k / nSteps)]]).T
    return u


# simulate new true robot position
def simulate_world(k):
    global xTrue
    u = get_robot_control(k)
    xTrue = tcomp(xTrue, u)
    xTrue[2, 0] = angle_wrap(xTrue[2, 0])


# computes and returns noisy odometry
def get_odometry(k):
    global xOdom  # internal to robot low-level controller
    global QTrue

    u = get_robot_control(k)
    xnow = tcomp(xOdom, u)
    uNoise = np.sqrt(QTrue) @ np.random.randn(3)
    uNoise = np.array([uNoise]).T
    xnow = tcomp(xnow, uNoise)
    xOdom = xnow
    u = u + uNoise
    return xnow, u


# generate a noisy observation of a random feature
def get_observation(k):
    global Map, xTrue, PYTrue
    iFeature = np.random.randint(0, Map.shape[1] - 1)
    zNoise = np.sqrt(PYTrue) @ np.random.randn(2)
    zNoise = np.array([zNoise]).T
    z = observation_model(xTrue, iFeature, Map) + zNoise
    z[1, 0] = angle_wrap(z[1, 0])
    
    return [z, iFeature]


# ---- model functions ----

# evolution model (f)
def motion_model(x, u):
    xPred = tcomp(x, u)
    xPred[2, 0] = angle_wrap(xPred[2, 0])
    return xPred


# observation model (h)
def observation_model(xVeh, iFeature, Map):
    Delta = Map[0:2, iFeature:(iFeature+1)]-xVeh[0:2]
    z = np.array([[np.linalg.norm(Delta)], [
        atan2(Delta[1], Delta[0]) - xVeh[2, 0]]])
    z[1, 0] = angle_wrap(z[1, 0])
    return z


# ---- Jacobian functions to be completed ----

# h(x) Jacobian wrt x
def get_obs_jac(xPred, iFeature, Map):
    jH = np.zeros((2, 3))
    
    # TODO
    print(observation_model(xPred, iFeature, Map))
    return jH


# f(x,u) Jacobian wrt x
def A(x, u):
    Jac = np.zeros((3, 3))

    #a = jacobian(motion_model(x,u))
    #print(a)
    # TODO

    return Jac


# f(x,u) Jacobian wrt u
def B(x, u):
    Jac = np.zeros((3, 3))

    # TODO

    return Jac


# ---- Gloabl variables ----

# Simulation length
nSteps = 6000

# Location of landmarks
Map = 140*np.random.rand(2, 30)-70

# True covariance of errors used for simulating robot movements
QTrue = np.diag([0.01, 0.01, 1*pi/180]) ** 2
PYTrue = np.diag([5.0, 6*pi/180]) ** 2

# Modeled errors used in the Kalman filter process
QEst = np.eye(3, 3) @ QTrue
PYEst = np.eye(2, 2) @ PYTrue

# initial conditions
xTrue = np.array([[1, -40, -pi/2]]).T
xOdom = xTrue
xEst = xTrue
PEst = 10 * np.diag([1, 1, (1*pi/180)**2])

# Init history matrixes
hxEst = xEst
hxTrue = xTrue
hxOdom = xOdom
hxError = np.abs(xEst-xTrue)  # pose error
hxVar = np.sqrt(np.diag(PEst).reshape(3, 1))  # state std dev


for k in range(1, nSteps):

    # Simlulate robot motion
    simulate_world(k)

    # Get odometry measurements
    xOdom, u = get_odometry(k)

    # Kalman prediction
    xPred = motion_model(xEst, u)  # function f
    PPred = A(xEst, u) @ PEst @ A(xEst, u).T + B(xEst, u) @ QEst @ B(xEst, u).T

    # Get random landmark observation
    [z, iFeature] = get_observation(k)

    if z is not None:
        # Predict observation
        zPred = observation_model(xPred, iFeature, Map)

        # get observation Jacobian
        H = get_obs_jac(xPred, iFeature, Map)

        # compute observation error (innovation)
        Innov = z-zPred
        Innov[1, 0] = angle_wrap(Innov[1, 0])

        # compute Kalman gain
        S = H @ PPred @ H.T + PYEst
        W = PPred @ H.T @ np.linalg.inv(S)

        # perform kalman update
        xEst = xPred + W @ Innov
        xEst[2, 0] = angle_wrap(xEst[2, 0])

        PEst = PPred - W @ H @ PPred
        PEst = 0.5 * (PEst + PEst.T)  # ensure symetry

    else:
        # there was no observation available
        xEst = xPred
        PEst = PPred

    # store data history
    hxTrue = np.hstack((hxTrue, xTrue))
    hxOdom = np.hstack((hxOdom, xOdom))
    hxEst = np.hstack((hxEst, xEst))
    err = xEst - xTrue
    err[2, 0] = angle_wrap(err[2, 0])
    hxError = np.hstack((hxError, err))
    hxVar = np.hstack((hxVar, np.sqrt(np.diag(PEst).reshape(3, 1))))

    # plot every 15 updates
    if show_animation and k % 200 == 0:
        # for stopping simulation with the esc key.
        plt.gcf().canvas.mpl_connect('key_release_event',
                    lambda event: [exit(0) if event.key == 'escape' else None])

        ax1.cla()

        # Plot true landmark and trajectory
        ax1.plot(Map[0, :], Map[1, :], "*k")
        ax1.plot(hxTrue[0, :], hxTrue[1, :], "-k", label="True")

        # Plot odometry trajectory
        ax1.plot(hxOdom[0, :], hxOdom[1, :], "-g", label="Odom")

        # Plot estimated trajectory an pose covariance
        ax1.plot(hxEst[0, :], hxEst[1, :], "-r", label="EKF")
        ax1.plot(xEst[0], xEst[1], ".r")
        plot_covariance_ellipse(xEst,
                                PEst, ax1, "--r")

        ax1.axis([-70, 70, -70, 70])
        ax1.grid(True)
        ax1.legend()

        # plot errors curves
        ax3.plot(hxError[0, :], 'b')
        ax3.plot(3.0 * hxVar[0, :], 'r')
        ax3.plot(-3.0 * hxVar[0, :], 'r')
        ax3.set_ylabel('x')

        ax4.plot(hxError[1, :], 'b')
        ax4.plot(3.0 * hxVar[1, :], 'r')
        ax4.plot(-3.0 * hxVar[1, :], 'r')
        ax4.set_ylabel('y')

        ax5.plot(hxError[2, :], 'b')
        ax5.plot(3.0 * hxVar[2, :], 'r')
        ax5.plot(-3.0 * hxVar[2, :], 'r')
        ax5.set_ylabel(r"$\theta$")

        plt.pause(0.001)

plt.savefig('EKFLocalization.png')
print("Press Q in figure to finish...")
plt.show()
