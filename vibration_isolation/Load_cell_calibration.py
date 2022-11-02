import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load data
data = pd.read_csv('load_cell_calibration_data.csv', index_col=None, header=0)

# Group the values by weight and calculate the stdev
grouped = data.groupby('Mass (g)')
grouped_avg = grouped.mean()

stdev = grouped.std()

# Calculate 1st order polynomial fit on the grouped_avg data
p, res, _, _, _ = np.polyfit(grouped_avg.index, grouped_avg['Sensor reading'], 1, full=True)
fit_stdev = 3 * np.sqrt(res[0]/(len(grouped_avg.index)-2))
fit_fn = np.poly1d(p)

# Plot the data with error bars
plt.errorbar(grouped_avg.index, grouped_avg['Sensor reading'], yerr=stdev['Sensor reading'], label='Measurement error', capsize=4, lw=0, elinewidth=1)
plt.fill_between(grouped_avg.index, grouped_avg['Sensor reading']-fit_stdev, grouped_avg['Sensor reading']+fit_stdev, alpha=0.2, color='gray', label='Fit error')
plt.plot(grouped_avg.index, fit_fn(grouped_avg.index), label='1st order fit', color='gray')
plt.scatter(grouped_avg.index, grouped_avg['Sensor reading'], label='Measurement', color='black', s=3)
plt.xlabel('Mass (g)')
plt.ylabel('Load cell reading (-)')
plt.legend()
plt.grid(True)
plt.show()