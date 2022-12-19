import numpy as np
import matplotlib.pyplot as plt
import scienceplots as sci

def amplitude(D, f):
    """
    Calculate the amplitude as a function of frequency.
    
    Parameters
    ----------
    D : float
        Damping ratio d/(2 * sqrt(mk)).
    f : float
        Frequency (Hz).

    Returns
    -------
    float
        Amplitude.
    """
    return np.sqrt(1 + (2*D*f)**2) / np.sqrt((1 - f**2)**2 + (2 * D * f)**2)

def phase(D, f):
    """
    Calculate the phase as a function of frequency.
    
    Parameters
    ----------
    D : float
        Damping ratio d/(2 * sqrt(mk)).
    f : float
        Frequency (Hz).

    Returns
    -------
    float
        Phase.
    """
    return np.arctan2((-2 * D * f**3), (1 - f**2 + (2 * D * f)**2))


if __name__ == '__main__':
    # Create the intervals
    damping_ratios = np.array([0.01, 0.1, 0.2, 0.5, 1, 2])
    frequencies = np.linspace(0.1, 10, 5000)

    # Create the graphs
    # plt.style.use(['science','ieee', 'no-latex'])
    
    fig, axs = plt.subplots(2, 1, sharex=True)

    for D in damping_ratios:
        axs[0].plot(frequencies, amplitude(D, frequencies), label=f'D = {D}')
        axs[1].plot(frequencies, phase(D, frequencies), label=f'D = {D}')

    # Set some aesthetics
    # plt.rcParams.update({"font.size":11})          # specify font size here
    axs[0].set_ylabel('Amplitude (-)')
    axs[0].set_yscale('log')
    axs[1].set_ylabel('Phase (rad)')
    axs[1].set_xscale('log')
    axs[1].set_xlabel('Frequency (Hz)')
    axs[0].legend(loc='upper right')
    axs[1].legend(loc='upper right')
    axs[0].grid(True)
    axs[1].grid(True)
    plt.show()

