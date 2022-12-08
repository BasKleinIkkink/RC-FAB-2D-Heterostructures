import control as c
import matplotlib.pyplot as plt
import numpy as np


# Initial system parameters
m = 70 # kg
k = 1000 # N/m
d = 100 # Ns/m

H = c.tf([d, k], [m, d, k])

# Create the frequensie response
#w, mag, phase = c.bode(H, dB=True, Hz=True, deg=True, plot=False)
#plt.show()

plt.clf()
fix, axs = plt.subplots(2, 1)

w0 = 1
m = 1
x = 10**2 * m
d_list = np.array([0.01, 0.1, 0.5, 1, 2])
for i in d_list:
    G = c.tf([i, x], [m, i, x])
    w, mag, phase = c.bode(G, dB=True, Hz=True, deg=True, plot=False)
    axs[0].plot(w, mag, label=f"D={round(i, 2)}")
    axs[1].plot(w, phase, label=f"D={round(i, 2)}")

axs[0].set_xscale('log')
axs[0].set_xlabel('Frequency [Hz]')
axs[0].set_ylabel('Magnitude [dB]')
axs[0].grid(True)
axs[0].legend()
plt.show()