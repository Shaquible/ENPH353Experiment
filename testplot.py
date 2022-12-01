import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.signal as signal
from scipy.fft import fft, fftfreq
from scipy.optimize import minimize


def getGainOffSet(S1, S2):
    # optimize gain of S1 so that S1 + S2 = constant and S1 - S2 = 0
    def calcGain(params):
        gain = params[0]
        offset = params[1]
        avg = np.mean(S2)
        return np.sum((S1*2 + S2 + offset - 2*avg)**2) + np.sum((S1*2 - S2 + offset)**2)
    # limit offset to 2
    res = minimize(calcGain, [2, 0], bounds=[(1, 10), (-5, 5)])
    gain = res.x[0]
    offset = res.x[1]
    print(gain, offset)
    return gain, offset


# read in the data
fname = 'finalSpin5.csv'
df = pd.read_csv(fname)
# convert to numpy array
data = df.to_numpy()
time = data[:, 0]
gyroZ = data[:, 1]
in2 = data[:, 2]-5
in1 = data[:, 3]-5
# cutoff overalocated space where all values are 0
cuttOffIdx = np.where(time == 0)
time = time[:cuttOffIdx[0][0]]
gyroZ = gyroZ[:cuttOffIdx[0][0]]
in2 = in2[:cuttOffIdx[0][0]]
in1 = (in1[:cuttOffIdx[0][0]])
staticTime = np.where(time > 5)[0][0]
gain, offset = getGainOffSet(in1[:staticTime], in2[:staticTime])
in1 = in1*gain + offset
#plt.plot(time, gyroZ, label='gyroZ')
plt.plot(time, in1, label='in1')
plt.plot(time, in2, label='in2')
plt.plot(time, in1+in2, label='in1+in2')
plt.plot(time, in1-in2, label='diff')
plt.legend()
plt.xlabel("Time (s)")
plt.ylabel("Signal (V)")
plt.show()
# plot a fft of in1
"""
N = len(in1)
T = 1/fs
yf = fft(in1)
xf = fftfreq(N, T)[:N//2]
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), 'bo', markersize=1)
plt.xlabel('Frequency [Hz]')
plt.grid()
plt.show()
"""
# filter the data to lowpass at 0.01 Hz
b, a = signal.butter(3, 0.005, 'low', analog=False)
in1_filt = signal.filtfilt(b, a, in1)
in2_filt = signal.filtfilt(b, a, in2)
# plot a fft of in1
"""
N = len(in1_filt)
T = 1/fs
yf = fft(in1_filt)
xf = fftfreq(N, T)[:N//2]
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), 'bo', markersize=1)
plt.xlabel('Frequency [Hz]')
plt.grid()
plt.show()
"""


def calcOmega(S1, S2, A, Lambda):
    Smax = S1 + S2
    Diff = S1 - S2
    c = 2.99792458e8
    deltaPhi = np.arcsin(-Diff/Smax)
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
plt.xlabel("Time (s)")
plt.ylabel("Angular Velocity (rad/s)")
plt.show()
