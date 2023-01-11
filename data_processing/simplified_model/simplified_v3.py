import numpy as np
import matplotlib.pyplot as plt
import scienceplots as sci

def amplitude(D, f):
    """Calculate the amplitude as a function of frequency."""
    return np.sqrt(1 + (2*D*f)**2) / np.sqrt((1 - f**2)**2 + (2 * D * f)**2)

def a2(D, f):
    return 1 / (1 - f**2)**2

def phi2(D, f):
    return np.arctan2(0, 1 - f**2)

def phase(D, f):
    """Calculate the phase as a function of frequency."""
    return np.arctan2((-2 * D * f**3), (1 - f**2 + (2 * D * f)**2))


def time_response(D, f, t):
    """Calculate the time response of the transfer function."""
    return np.exp(-D * f * t) * np.sin(f * np.sqrt(1 - D**2) * t)


def D(d, m, k):
    """Calculate the damping ratio from the damping constant."""
    return d / (2 * np.sqrt(m * k))


def f(w, m, k):
    """Calculate the frequency from the angularand eigen frequency."""
    return w / (2 * np.pi * np.sqrt(m / k))


if __name__ == '__main__':
    # Set system parameters
    m = 73  # kg
    k = 69  # N/m
    d = 0  # Ns/m

    # Create the intervals
    omega = np.linspace(0.1, 100, 1000)
    damping_ratio = np.array([0, 0.01, 0.1, 0.5], dtype=float)
    # damping_ratios = np.array([0.01, 0.1, 0.2, 0.5, 1, 2])
    frequencies = f(omega, m, k)

    # Create the graphs
    plt.style.use(['science','ieee'])
    fig, axs = plt.subplots(2, 1, sharex=True)
    t = np.linspace(0, 100, 10000)

    for d in damping_ratio:
        axs[0].plot(frequencies, amplitude(d, frequencies), label=f'D = {d}')
        axs[1].plot(frequencies, phase(d, frequencies), label=f'D = {d}')

    # Set some aesthetics
    axs[0].set_ylabel('$Amplitude\quad \mathrm{(-)}$')
    axs[0].set_yscale('log')
    axs[1].set_ylabel('$Phase\quad \mathrm{(rad)}$')
    axs[1].set_xscale('log')
    axs[1].set_xlabel('$Frequency\quad \mathrm{(Hz)}$')
    axs[0].legend(loc='upper left')
    axs[1].legend(loc='upper left')
    axs[0].grid(True)
    axs[1].grid(True)
    
    plt.savefig('1dof_oscillator_without_damping.png', dpi=500, bbox_inches='tight')

