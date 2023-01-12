import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import time
import json
import scienceplots
import datetime



class GridConditions:
    """
    Class to determine the constants for a point in the grid.
    
    The class governs the used constants by each gridpoint by their
    position in the grid.
    """
    state = 'SOLID'
    if state not in ['SOLID', 'REDUCED']:
        raise TypeError('The model type should either be SOLID or REDUCED, not {}'.format(state))
    reduction_factor = 0.4  # 40% mass reduction
    position = 0  # Position given in grid spacing
    h = 0.25e-3  # Time step in s

    # D = specific_heat/(conductivity * density)
    N = 300  # Number of intervals on the grid
    Dal = 237 / (2700 * 903)
    Dn = 0.024 / (1024 * 1.25)
    _lal = 0.025  # Radius of the cilinder in m
    L = 1  # Length of the space in m
    _TAl0 = 40 # Starting temperature of the aluminium in C 
    TN0 = 22  # Starting temperature of the nitrogen in C 
    t_list = [round(i/2, 2) for i in range(2 * 5 * 60)]  # List of checkpoints in s
    t_list = [0.01, 60, 180, 300]	
    a = L/N  # Lenght of bar in one grid spacing

    def __init__(self) -> ...:
        """Initiate the model parameters."""
        ral = (2 * self.lal)/self.L * self.N
        self.switch_points = [int(1/2 * self.N - ral), int(1/2 * self.N + ral)]
        
    @property
    def D(self) -> float:
        """The thermal diffusion constant of the current gridpoint."""
        if self.position < self.switch_points[0] or \
                self.position > self.switch_points[1]:
            return self.Dn
        else:
            return self.Dal

    @property
    def lal(self) -> float:
        """The radius of the aluminum cylinder in m."""
        if self.state == 'SOLID':
            return self._lal
        elif self.state == 'REDUCED':
            return self._lal * (1 - self.reduction_factor)

    @property
    def TAl0(self) -> float:
        """The starting temperature of the aluminum in C."""
        return self._TAl0
        

def run_model(conditions):
    """
    Run the model and return the data.
    
    The settings for the model are set using the 
    :class:`GridConditions` class.

    Parameters
    ----------
    conditions : GridConditions
        The conditions for the model.
    """
    e = par.h / 1000  # Error margin to reduce floating point errors
    C = par.h / par.a**2  # A precalculated constant for the calculation

    print('{} timesteps, {} gridpoints = {} calculations'.format(par.t_list[-1]/par.h, par.N,
                                                                 par.t_list[-1]/par.h * par.N))

    # Create the starting and buffer array
    border = par.switch_points
    T = np.empty(par.N + 1, dtype=float)
    T[border[0]: border[1]] = par.TAl0
    T[border[1]:] = par.TN0
    T[:border[0]] = par.TN0
    Tb = np.empty(par.N + 1, dtype=float)
    Tb[border[0]: border[1]] = par.TAl0
    Tb[border[1]:] = par.TN0
    Tb[:border[0]] = par.TN0

    #############
    # Main loop #
    #############
    t = 0.0  # s
    te = par.t_list[-1] + e
    data = []
    while t < te:
        # Calculate the temperature after the next time step
        for i in range(1, par.N):
            # Fill the buffer array with the new data
            par.pos = i
            Tb[i] = T[i] + C * par.D*(T[i+1] + T[i-1] - 2* T[i])
        T, Tb = Tb, T  # Switch the arrays buffer is now most recent
        t += par.h  # Increase the time
        
        # Check if any of the checkpoints were reached
        for tc in par.t_list:
            if abs(t - tc) < e:
                # Reverse the arrays to get the correct order
                Td = T.copy()
                data.append((tc, Td))
                par.t_list.remove(tc)

    return data


def save_data(filename) -> ...:
    """Save the data to a file."""
    content = {}
    for tc, Td in data:
        content[tc] = Td.tolist()

    with open(filename, 'w') as f:
        json.dump(content, f)


def load_data(filename) -> list:
    """Load the data from the data file."""
    with open(filename, 'r') as f:
        content = json.load(f)
    data = []
    for tc, Td in content.items():
        data.append((float(tc), np.array(Td)))
    return data


if __name__ == '__main__':
    filename = str(datetime.datetime.now()).replace(':', ',')   
    par  = GridConditions()
    data = run_model(par)
    #data = load_data(filename)

    plt.style.use(['science', 'ieee'])
    x = np.linspace(0, par.L, par.N + 1)
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(MaxNLocator())
    ax.set_xlabel('$x\quad \mathrm{(m)}$')
    ax.set_ylabel('$Temperature\quad \mathrm{(C)}$')
    for tc, Td in data:
        ax.plot(x, Td, label='t = {} s'.format(tc))
    ax.legend()
    ax.grid(True)
    plt.savefig(filename+'.png', bbox_inches='tight', dpi=500)
    save_data(filename+'.json')

