import pandas as pd
import os
import matplotlib.pyplot as plt

# Read in the data
path = os.path.dirname(os.path.abspath(__file__)) + '\\temp_data.csv'
df = pd.read_csv(path, skiprows=8).iloc[:, :4]
samplerate = 0.5  # Hz
df['time'] = df.index / samplerate


# Plot te data
fig, ax = plt.subplots()
ax.plot(df['time'], df['T1 (°C)'], label='Sample bed surface')
ax.plot(df['time'], df['T2 (°C)'], label='Cilinder')
ax.plot(df['time'], df['T3 (°C)'], label='Rotation stage')
ax.grid(True)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Temperature (°C)')
ax.legend(loc='upper right')
plt.show()