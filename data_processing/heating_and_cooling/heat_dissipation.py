import pandas as pd
import matplotlib.pyplot as plt
import scienceplots
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
    low_temp_data = os.path.join(dir_path, 'metingen/heat_dissipation_40C.csv')

    df = pd.read_csv(low_temp_data, skiprows=8).iloc[25: , :]
    df['t'] = [round(i/2, 1) for i in range(len(df.index * 2))]
    
    plt.style.use(['science', 'ieee'])
    fig, ax = plt.subplots()
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Temperature (C)')
    # plt.plot(df['t'], df['T1 (°C)'], label='T1')
    plt.plot(df['t'], df['T2 (°C)'], label='Spacer bus')
    plt.plot(df['t'], df['T3 (°C)'], label='Rotation stage')

    plt.grid(True)
    plt.legend(loc='best')
    plt.savefig('low_temp_dissipation_measurement.png', dpi=500)