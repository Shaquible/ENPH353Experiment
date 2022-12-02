import time
import adafruit_mpu6050
import board
import numpy as np
import RPi.GPIO
import busio
import ADS1256
import argparse

i2c = board.I2C()
mpu = adafruit_mpu6050.MPU6050(i2c)
ADC = ADS1256.ADS1256()
ADC.ADS1256_init()

def parse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('numSec', type=int, help='Number of seconds to record data')
    parser.add_argument('fileName', type=str)
    args=parser.parse_args()
    return args

args = parse_input()

def recordGyroData(numSec):
    # Record data for numSec seconds
    data = np.zeros((round(numSec*150), 4))
    startTime = time.time()
    i = 0
   
    correct = 5/(2**23)
    while time.time() - startTime < numSec:
        dt = time.time() - startTime
        data[i, :] = [dt, mpu.gyro[2], ADC.ADS1256_GetChannalValue(1)*correct, ADC.ADS1256_GetChannalValue(2)*correct]
        i += 1
        #print(dt)
    return data
# run the two data collection functions on parallel cores

#print(args.fileName)

data = recordGyroData(args.numSec)
np.savetxt('SagnacData/' + args.fileName + '.csv', data, delimiter=',')
