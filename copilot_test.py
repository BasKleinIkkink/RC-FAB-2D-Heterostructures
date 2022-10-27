import scipy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter


#Model the magnetic field of a solenoid	
def B_solenoid(r, I, N, a):
    mu_0 = 4 * np.pi * 10**-7
    B = mu_0 * I * N * (a**2 / (2 * (r**2 + a**2)**(3/2)))
    return B

#plot a 3D graph of the magnetic field of a solenoid
def plot_solenoid(r, I, N, a):
    x = np.linspace(-r, r, 100)
    y = np.linspace(-r, r, 100)
    X, Y = np.meshgrid(x, y)
    Z = B_solenoid(np.sqrt(X**2 + Y**2), I, N, a)
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
    ax.set_zlim(-1.01, 1.01)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()

#create random data for a solenoid function and plot it
def random_solenoid():
    r = np.random.randint(1, 100)
    I = np.random.randint(1, 100)
    N = np.random.randint(1, 100)
    a = np.random.randint(1, 100)
    plot_solenoid(r, I, N, a)

#use the methods above to generate a nice plot
def main():
    random_solenoid()

main()