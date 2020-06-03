import serial
ser = serial.Serial('/dev/ttyS0',9600)
while True:
	read_serial=ser.readline()
	print(read_serial)