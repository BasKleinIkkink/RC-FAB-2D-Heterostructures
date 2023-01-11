import pandas as pd
import os
import matplotlib.pyplot as plt
import scienceplots

# Read in the data
path = os.path.dirname(os.path.abspath(__file__)) + '\\metingen\\thermal_cycle_reduced.csv'
df = pd.read_csv(path, skiprows=8).iloc[:, :4]



samplerate = 0.5  # Hz
df['time'] = df.index / samplerate
df = df.drop(df.index[:int(1450)])


# Plot te data
plt.style.use(['science', 'ieee'])
fig, ax = plt.subplots()
ax.plot(df['time'], df['T1 (°C)'], label='$Sample bed$')
ax.plot(df['time'], df['T2 (°C)'], label='$Cylinder$')
ax.plot(df['time'], df['T3 (°C)'], label='$Rotation$')
ax.grid(True)
ax.set_xlabel('$Time\quad \mathrm{(s)}$')
ax.set_ylabel('$Temperature\quad \mathrm{(°C)}$')
ax.legend(loc='upper right')
plt.savefig('test.png', dpi=500)