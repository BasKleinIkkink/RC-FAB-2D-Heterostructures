# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 19:35:53 2022

@author: baskl
"""
import numpy as np
import matplotlib.pyplot as plt
import locale
import seaborn as sns

locale.setlocale(locale.LC_NUMERIC, 'de_DE.UTF-8')  # Set comma for decimals
plt.rcParams['axes.formatter.use_locale'] = True
sns.set(rc={'text.usetex': True})  # Turn on the LaTeX interpreter
sns.set_style('whitegrid')  # Set the graph grid to white

# Define the bar parameters
L = 0.01  # Length of the bar in m
N = 100  # Number of intervals on the grid
a = L/N  # Lenght of bar in one grid spacing
h = 1e-4  # Time step in s
e = h / 1000  # Error margin to reduce floating point errors

# Define the starting parameters
D = 4.25e-6  # Thermal deffusion constant
T0 = 0  # Starting temperature left in C
Tn = 50  # Starting temperature right in C
Ts = 25  # Starting temperatur of the rest in C
C = h * D / a**2  # A precalculated constand for the calculation

# Create the starting and buffer array
T = np.empty(N + 1, dtype=float)
T[0] = T0
T[N] = Tn
T[1:N] = Ts
Tb = np.empty(N + 1, dtype=float)
Tb[0] = T0
Tb[N] = Tn

# Run the main loop
t_list = [0.01, 0.1, 0.4, 4]
t = 0.0  # s
te = t_list[-1] + e
x = np.linspace(0, L, N + 1)

while t < te:
    # Calculate the temperature after the next time step
    for i in range(1, N):
        # Fill the buffer array with the new data
        Tb[i] = Tb[i] = T[i] + C*(T[i+1] + T[i-1] - 2* T[i])
    T, Tb = Tb, T  # Switch the arrays buffer is now most recent
    t += h  # Increase the time
    
    # Check if any of the checkpoints were reached
    for tc in t_list:
        if abs(t - tc) < e:
            label = '$t = \; {}\; \mu s$'.format(tc)
            plt.plot(x, T, label=label)
            t_list.remove(tc)
            

plt.legend(loc='best')
plt.xlabel('$x\; \mathrm{(m)}$')
plt.ylabel('$Temperature\; \mathrm{(C)}$')
plt.grid(True)
plt.show()
        
            
