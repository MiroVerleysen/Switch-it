import serial

ser = serial.Serial('/dev/ttyS0',9600)
ser.flushInput()

while True:
    print("{0}".format(ser.readline()))