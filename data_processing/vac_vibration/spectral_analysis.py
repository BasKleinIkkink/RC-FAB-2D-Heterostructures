import pandas as pd
import os
import matplotlib.pyplot as plt
from quick_fft_filter import quick_process

dir = os.path.abspath(os.path.dirname(__file__)) + '\\data_files\\'
files = os.listdir('data_processing/vac_vibration/data_files')


if __name__ == '__main__':
    df = pd.read_csv(dir + files[0], skiprows=5).iloc[: ,:-1]
    x = len(df['Vertical (V)'])
    df = df.iloc[:int(x/2), :]
    print(df.head())

    samplerate = 2048  # Hz
    # freq, psd = signal.welch(df['Vertical (V)'], samplerate)
    # fhat = fft.fft(df['Vertical (V)'])  # compute the FFT

    ffilt, L, freq, PSD, PSDclean = quick_process(samplerate, df['Vertical (V)'].to_numpy())

    plt.show()
    
