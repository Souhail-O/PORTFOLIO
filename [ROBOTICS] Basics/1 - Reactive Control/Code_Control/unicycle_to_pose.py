#!/bin/env python3


"""

TP Reactive control for mobile robots

author: Alexandre Chapoutot and David Filliat

"""
import math

import numpy as np
import matplotlib.pyplot as plt

import vehicle_model as vm


# Parameters
show_animation = True
nbTest = 10

k_rho = 15 #7.5
k_alpha = 10 #0.75
k_beta = 20 #.5
alpha_max = 1.2 #0.05

# Compute control
def unicycle_to_pose_control(xTrue, xGoal):
    """
    Compute control from current pose and goal pose
    Input:
    - xTrue : current [x, y, \theta] robot pose
    - XGoal : [x, y, \theta] goal pose
    Output:
    - u : [v, \omega] control: translation and rotation speed
    """
    u = np.array([0.0, 0.0])

    rho = np.sqrt( ( xGoal[0] - xTrue[0] )**2 + ( xGoal[1] - xTrue[1] )**2 )

    alpha = np.arctan2 ( ( xGoal[1] - xTrue[1] ) , ( xGoal[0] - xTrue[0] )) - xTrue[2]

    alpha = vm.angle_wrap(alpha)

    if abs(alpha) > alpha_max : 
        u[0] = 0
    else :
        u[0] = k_rho * rho

    if rho < 0.05 : 

        u[1] = (xGoal[2] - xTrue[2]) * k_beta
        
    else : 
        u[1] = k_alpha * alpha
        

    return u


# Main function
def main():
    print("reactive control of Unicycle start")

    Perf = []

    # loop from starting positions
    for i in range(nbTest):

        xGoal = np.array([0.0, 0.0, 0.0])
        xTrue = np.array([2.0 * np.cos(2*np.pi*i/nbTest),
                          2.0 * np.sin(2*np.pi*i/nbTest),
                          2*np.pi*i/nbTest])

        # Initial speed and angle
        v = 0
        w = 0

        if show_animation:
            # for stopping simulation with the esc key.
            plt.gcf().canvas.mpl_connect('key_release_event',
                    lambda event: [exit(0) if event.key == 'escape' else None])
            plt.grid(True)
            plt.axis("equal")

        if show_animation:
            # display xGoal
            vm.plot_arrow(xGoal[0], xGoal[1], xGoal[2], fc='b')
            # display initial position
            vm.plot_arrow(xTrue[0], xTrue[1], xTrue[2], fc='r')

        k = 0
        while np.amax(np.absolute(vm.dist(xTrue, xGoal))) > 0.06 and k < 10000:
            # Compute Control
            u = unicycle_to_pose_control(xTrue, xGoal)

            # Simulation of the vehicle motion
            [xTrue, u, v, w] = vm.simulate_unicycle(xTrue, u, v, w)

            if show_animation:
                if k % 150 == 1:
                    vm.plot_arrow(xTrue[0], xTrue[1], xTrue[2], fc='g')
                    plt.plot(xTrue[0], xTrue[1], ".g")
                    plt.pause(0.0001)

            k = k + 1

        # Store performances
        Perf.append(k)

    # Display mean performances
    print('Mean goal reaching steps : ', np.mean(Perf))

    if show_animation:
        plt.savefig('unicycle_to_pose.png')
        print('Finished. Press Q in window to exit.')
        plt.show()


if __name__ == '__main__':
    print(__file__ + " start!!")
    main()
    print(__file__ + " Done!!")
