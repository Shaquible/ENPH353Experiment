from scipy.signal import butter, lfilter
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# read in the data
fname = 'testdata_60.csv'
gain = 3.5
df = pd.read_csv(fname)
# convert to numpy array
data = df.to_numpy()
time = data[:, 0]
gyroZ = data[:, 1]
in2 = 5-data[:, 3]
in1 = (5-data[:, 4])*gain

# cutoff overalocated space where all values are 0
cuttOffIdx = np.where(gyroZ == 0)
time = time[:cuttOffIdx[0][0]]
gyroZ = gyroZ[:cuttOffIdx[0][0]]
in2 = in2[:cuttOffIdx[0][0]]
in1 = in1[:cuttOffIdx[0][0]]
# filter the signal with a rolling average of 25 samples
window = 25
in1Avg = pd.Series(in1).rolling(window).mean()
in2Avg = pd.Series(in2).rolling(window).mean()


def calcOmega(S1, S2, A, Lambda):
    Smax = S1 + S2
    Diff = S1 - S2
    c = 2.99792458e8
    deltaPhi = np.arccos(Diff/Smax)
    omega = deltaPhi/(8*A*np.pi)*Lambda*c
    return omega


# calculate the angular velocity
A = 0.634*0.438
omega = calcOmega(in1Avg, in2Avg, A, 632.8e-9)
plt.plot(time, omega, "bo", label='omega', markersize=1)
plt.plot(time, gyroZ, label='gyroZ')
plt.legend()
plt.show()
