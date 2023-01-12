import numpy as np
from quick_fft_filter import quick_process


filename = 'vibration_isolation\data.csv'
data = np.loadtxt(filename, delimiter=',', skiprows=0)
results = quick_process(data=data[:, 0], samplerate=30)