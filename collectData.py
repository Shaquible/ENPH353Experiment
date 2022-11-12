import time
import adafruit_mpu6050
import board
import busio
import numpy as np
from qredpitaya import ConnectRedPitaya, convert_scpi_list_to_array
import multiprocessing

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)
PORT = 5000
IP = "192.168.0.31"


def recordGyroData(numIter):
    numSec = numIter*8.59
    # Record data for numSec seconds
    data = np.zeros((numSec*3000, 2))
    startTime = time.time()
    i = 0
    while time.time() - startTime < numSec:
        data[i, :] = [startTime-time.time(), mpu.gyro[2]]
        i += 1
    return data


def recordPitaya(numIter):
    adc_decimation = 65536
    tmaster = np.arange(0, numIter*16383*8.0e-9*adc_decimation, numIter*8.0e-9*adc_decimation)
    v1Master = np.arange(0, numIter*16383*8.0e-9*adc_decimation, numIter*8.0e-9*adc_decimation)
    v2Master = np.arange(0, numIter*16383*8.0e-9*adc_decimation, numIter*8.0e-9*adc_decimation)
    for i in range(numIter):
        rp = ConnectRedPitaya(IP, port=PORT, verbose=True)
        rp.flush()
        rp('ACQ:RST')
        rp('ACQ:DATA:FORMAT ASCII')
        rp('ACQ:DATA:UNITS VOLTS')
        # 1, 8, 64, 1024, 8192, 65536
        rp("ACQ:DEC {adc_decimation}".format(**locals()))

        rp('ACQ:TRIG:LEV 0.01')
        rp('ACQ:TRIG:LEV 0.01')

        rp('ACQ:START')
        rp('ACQ:TRIG CH2_PE')
        # time.sleep(1.05)

        while 1:
            time.sleep(0.05)
            if rp('ACQ:TRIG:STAT?') == 'TD':
                break

        # FUTURE BETA
        # while 1:
        #     rp_s.tx_txt('ACQ:TRIG:FILL?')
        #     if rp_s.rx_txt() == '1':
        #         break

        # time.sleep(1.05)

        buff_string = rp('ACQ:SOUR1:DATA?')
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        v1 = np.asarray(buff_string, dtype=float)

        buff_string = rp('ACQ:SOUR2:DATA?')
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        np.array(map(float, buff_string))
        v2 = np.asarray(buff_string, dtype=float)
        # put data into master arrays
        v1Master[i*16383:(i+1)*16383] = v1
        v2Master[i*16383:(i+1)*16383] = v2

    print("Stopping Acquire Module...")
    rp('ACQ:RST')
    if rp('ACQ:TRIG:STAT?') == "TD":
        print("Stopped.")
    else:
        print("Could not stop!")


# run the two data collection functions on parallel cores
if __name__ == '__main__':
    with multiprocessing.Pool(processes=2) as pool:
        gyroData = pool.apply_async(recordGyroData, [1])
        pitayaData = pool.apply_async(recordPitaya, [1])
        pool.join()
        pool.close()
