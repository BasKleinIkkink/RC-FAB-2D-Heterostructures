import control as c
import matplotlib.pyplot as plt
import numpy as np


# Initial system parameters
k = 1000 # N/m
m = 10 # kg
d = 10 # Ns/m
s = c.TransferFunction.s

# Create the transfer function
H = c.TransferFunction([d, k], [m ,k, d])
# H =  (k + s * d) / (m * s**2 + k + s * d)

# Calculate some response data
#mag, phase, omega = c.bode_plot(H, dB=True, Hz=True)
#T, yout = c.step_response(sys=H)
c.root_locus(H)

# Step response
#fig, ax = plt.subplots()
#ax.plot(T, yout)
#ax.set_title("Step response")
#ax.set_ylabel("Amplitude")
#ax.set_xlabel("Time [s]")
#ax.legend(loc='best')



plt.show()
