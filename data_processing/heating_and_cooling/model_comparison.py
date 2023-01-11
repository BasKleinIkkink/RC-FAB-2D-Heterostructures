import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
# import scienceplots
import json
import pandas as pd
# plt.style.use(['science', 'ieee'])


def load_data(filename):
    """Load the data from the data file."""
    with open(filename, 'r') as f:
        content = json.load(f)
    data = pd.DataFrame.from_dict(data=content, orient='index')
    return data


if __name__ == '__main__':
    solid_data = 'data_processing/heating_and_cooling/model_data/solid_cylinder_every_half_s.json'
    reduced_data = 'data_processing/heating_and_cooling/model_data/reduced_cylinder_every_half_s.json'
    solid = load_data(solid_data)
    reduced = load_data(reduced_data)

    # Plot column 100 for both dataframes
    df = pd.DataFrame({'solid': solid[100], 'reduced': reduced[100]})
    df['diff'] = df['reduced'] - df['solid']

    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(MaxNLocator())
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Temperature [C]')
    plt.plot(df.index, df['solid'], label='Solid')
    plt.plot(df.index, df['reduced'], label='Reduced')

    # Plot the diff a secondary axis
    
    plt.plot(df.index, df['diff'], label='Difference')
    plt.grid(True)
    plt.legend()
    plt.show()

