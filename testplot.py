import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.signal as signal
from scipy.fft import fft, fftfreq
# read in the data
fname = 'testdata_stat5.csv'
df = pd.read_csv(fname)
# convert to numpy array
data = df.to_numpy()
time = data[:, 0]
gyroZ = data[:, 1]
in2 = 5-data[:, 3]
in1 = (5-data[:, 4])
# cutoff overalocated space where all values are 0
cuttOffIdx = np.where(time == 0)
time = time[:cuttOffIdx[0][0]]
gyroZ = gyroZ[:cuttOffIdx[0][0]]
in2 = in2[:cuttOffIdx[0][0]] + 2.826679015285912
in1 = in1[:cuttOffIdx[0][0]]
"""
plt.plot(time, gyroZ, label='gyroZ')
plt.plot(time, in1, label='in1')
plt.plot(time, in2, label='in2')
plt.plot(time, in1+in2, label='in1+in2')
plt.plot(time, in1-in2, label='diff')
plt.legend()
plt.show()
"""
fs = 1/(np.mean(time[1:]-time[:-1]))
# plot a fft of in1
N = len(in1)
T = 1/fs
yf = fft(in1)
xf = fftfreq(N, T)[:N//2]
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), 'bo', markersize=1)
plt.xlabel('Frequency [Hz]')
plt.grid()
plt.show()

# filter the data to lowpass at 0.01 Hz
b, a = signal.butter(3, 0.005, 'low', analog=False)
in1_filt = signal.filtfilt(b, a, in1)
in2_filt = signal.filtfilt(b, a, in2)
# plot a fft of in1
N = len(in1_filt)
T = 1/fs
yf = fft(in1_filt)
xf = fftfreq(N, T)[:N//2]
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), 'bo', markersize=1)
plt.xlabel('Frequency [Hz]')
plt.grid()
plt.show()

plt.plot(time, in1, label='in1')
plt.plot(time, in1_filt, label='in1_filt')
plt.plot(time, in2, label='in2')
plt.plot(time, in2_filt, label='in2_filt')
plt.plot(time, in1_filt+in2_filt, label='in1+in2')
plt.plot(time, in1_filt-in2_filt, label='diff')
plt.legend()
plt.show()


def calcOmega(S1, S2, A, Lambda):
    Smax = S1 + S2
    Diff = S1 - S2
    c = 2.99792458e8
    deltaPhi = np.arcsin(Diff/Smax)
    omega = deltaPhi/(8*A*np.pi)*Lambda*c
    return omega


# calculate the angular velocity
A = 0.634*0.438
omega = calcOmega(in1_filt, in2_filt, A, 632.8e-9)
plt.plot(time, omega, "bo", label='omega', markersize=1)
plt.plot(time, gyroZ, label='gyroZ')
omegaUnfilt = calcOmega(in1, in2, A, 632.8e-9)
plt.plot(time, omegaUnfilt, "ro", label='omegaUnfilt', markersize=1)
plt.legend()
plt.show()
