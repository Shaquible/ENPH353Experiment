import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# read in the data
fname = 'testdata_stat2.csv'
df = pd.read_csv(fname)
# convert to numpy array
data = df.to_numpy()
time = data[:, 0]
gyroZ = data[:, 1]
in2 = 5-data[:, 3]
in1 = (5-data[:, 4])
# cutoff overalocated space where all values are 0
cuttOffIdx = np.where(gyroZ == 0)
time = time[:cuttOffIdx[0][0]]
gyroZ = gyroZ[:cuttOffIdx[0][0]]
in2 = in2[:cuttOffIdx[0][0]]
in1 = in1[:cuttOffIdx[0][0]]
plt.plot(time, gyroZ, label='gyroZ')
plt.plot(time, in1, label='in1')
plt.plot(time, in2, label='in2')
plt.legend()
plt.show()
