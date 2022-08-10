#!/bin/env python3

"""

TP Reactive control for mobile robots

author: Alexandre Chapoutot and David Filliat

"""
import math

import numpy as np
import matplotlib.pyplot as plt


# Parameters
show_animation = True


# Util functions
def angle_wrap(a):
    while a > np.pi:
        a = a - 2.0 * np.pi
    while a < -np.pi:
        a = a + 2.0 * np.pi
    return a


def dist(xTrue, xGoal):
    error = xGoal - xTrue
    if error.size == 3:
        error[2] = angle_wrap(error[2])
    return error


def plot_arrow(x, y, yaw, length=0.1, width=0.05, fc="r", ec="k"):
    """
    Plot arrow
    """

    if not isinstance(x, float):
        for (ix, iy, iyaw) in zip(x, y, yaw):
            plot_arrow(ix, iy, iyaw)
    else:
        plt.arrow(x, y, length * math.cos(yaw), length * math.sin(yaw),
                  fc=fc, ec=ec, head_width=width, head_length=width)
        plt.plot(x, y)


def simulate_bicycle(xTrue, u, v, phi):

    dt = 0.001  # integration time
    dVMax = 0.01  # limit linear acceleration
    dPhiMax = 0.008  # limit angular acceleration

    # limit acceleration
    delta_v = min(u[0] - v, dVMax)
    delta_v = max(delta_v, -dVMax)
    delta_phi = min(u[1] - phi, dPhiMax)
    delta_phi = max(delta_phi, -dPhiMax)
    v = v + delta_v
    phi = phi + delta_phi

    # limit control
    v = min(1.0, v)
    v = max(-1.0, v)
    phi = min(1.2, phi)
    phi = max(-1.2, phi)
    u = np.array([v, phi])

    # update state
    state = [xTrue[0] + v * dt * np.cos(xTrue[2]),
             xTrue[1] + v * dt * np.sin(xTrue[2]),
             angle_wrap(xTrue[2] + v / 0.5 * dt * np.tan(phi))]
    u = [v, phi]
    return (state, u, v, phi)


def simulate_unicycle(xTrue, u, v, w):

    dt = 0.001  # integration time
    dVMax = 0.01  # limit linear acceleration
    dWMax = 0.01  # limit angular acceleration

    # limit acceleration
    delta_v = min(u[0] - v, dVMax)
    delta_v = max(delta_v, -dVMax)
    delta_w = min(u[1] - w, dWMax)
    delta_w = max(delta_w, -dWMax)
    v = v + delta_v
    w = w + delta_w

    # limit control
    v = min(1, v)
    v = max(-1, v)
    w = min(np.pi, w)
    w = max(-np.pi, w)
    u = np.array([v, w])

    # update state
    state = np.array([xTrue[0] + v * dt * np.cos(xTrue[2]),
                      xTrue[1] + v * dt * np.sin(xTrue[2]),
                      angle_wrap(xTrue[2] + w * dt)])
    return (state, u, v, w)
