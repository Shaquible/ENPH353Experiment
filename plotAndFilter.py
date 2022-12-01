from scipy.signal import butter, lfilter
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import minimize
# read in the data
fname = 'newStat1.csv'
gain = 3.5
df = pd.read_csv(fname)
# convert to numpy array
data = df.to_numpy()
time = data[:, 0]
gyroZ = data[:, 1]
in2 = data[:, 2]-5
in1 = data[:, 3]-5
# optimize gain and offset so in1 + in2 = 1


def getGainOffSet(S1, S2):
    # optimize gain of S1 so that S1 + S2 = constant and S1 - S2 = 0
    def calcGain(params):
        gain = params[0]
        offset = params[1]
        return np.sum((S1*gain + S2 + offset + 2*2)**2) + np.sum((S1*gain - S2 + offset)**2)
    # limit offset to 2
    res = minimize(calcGain, [1, -1.00], bounds=[(1, 10), (-5, 5)])
    gain = res.x[0]
    offset = res.x[1]
    return gain, offset


    # cutoff overalocated space where all values are 0
cuttOffIdx = np.where(gyroZ == 0)
time = time[:cuttOffIdx[0][0]]
gyroZ = gyroZ[:cuttOffIdx[0][0]]
in2 = in2[:cuttOffIdx[0][0]]
in1 = in1[:cuttOffIdx[0][0]]
print(np.mean(in1))
print(np.mean(in2))
# filter the signal with a rolling average of 25 samples
window = 15
in1Avg = pd.Series(in1).rolling(window).mean()
in2Avg = pd.Series(in2).rolling(window).mean()
param = np.loadtxt('gainOffset.txt', delimiter=' ')
gain = param[0]
offset = param[1]
in1Avg = in1Avg*gain + offset
# calculate the gain and offset

gain, offset = getGainOffSet(in1, in2)
print(gain, offset)
# record gain and offset in a file
f = open("gainOffset.txt", "w")
f.write(str(gain) + " " + str(offset))
f.close()
in1 = in1*gain + offset
plt.plot(time, in1, label='in1')
plt.plot(time, in2, label='in2')
plt.plot(time, in1+in2, label='in1+in2 filtered')
plt.plot(time, in1-in2, label='diff')
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
omega = calcOmega(in1Avg, in2Avg, A, 632.8e-9)
plt.plot(time, omega, "bo", label='omega', markersize=1)
plt.plot(time, gyroZ, label='gyroZ')
plt.legend()
plt.show()
