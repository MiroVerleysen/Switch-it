# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from helpers.klasseIR import InfraRood
from helpers.klassemcp import mcp
from datetime import datetime
import time
from subprocess import check_output
import threading

# Code voor led
from helpers.klasseknop import Button
from RPi import GPIO

# Definieren LCD pinnen
LCD_RS = 21
LCD_E  = 20
LCD_D4 = 23
LCD_D5 = 26
LCD_D6 = 19
LCD_D7 = 13

count = 0
status = ""
# LCD constantes definieren
LCD_WIDTH = 16    # Maximum characters per lijn
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM 1e lijn
LCD_LINE_2 = 0xC0 # LCD RAM 2e lijn

# Definieren pinnen
relais = 6
rood = 22
groen = 27
# Oproepen klassen 
knop1 = Button(5)
ir = InfraRood(18)


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relais, GPIO.OUT)
GPIO.setup(rood, GPIO.OUT)
GPIO.setup(groen, GPIO.OUT)
GPIO.setup(LCD_E, GPIO.OUT)
GPIO.setup(LCD_RS, GPIO.OUT)
GPIO.setup(LCD_D4, GPIO.OUT)
GPIO.setup(LCD_D5, GPIO.OUT)
GPIO.setup(LCD_D6, GPIO.OUT)
GPIO.setup(LCD_D7, GPIO.OUT)
 



app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

@app.route('/read_all')
def ophalen_sensoren_data():
    output = DataRepository.read_all_sensors()
    return jsonify(data = output), 200

@app.route('/read_sensor/<sensorID>')
def ophalen_sensor_data(sensorID):
    output = DataRepository.read_sensor_by_id_one(sensorID)
    return jsonify(data = output), 200

@app.route('/read_sensor_recent/<sensorID>')
def ophalen_sensor_recent_data(sensorID):
    output = DataRepository.read_sensor_by_id_recent(sensorID)
    return jsonify(data = output), 200

@app.route('/read_actuator/<actuatorID>')
def ophalen_actuator_data(actuatorID):
    output = DataRepository.read_status_actuator_by_id(actuatorID)
    return jsonify(data = output), 200

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(0.0005)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(0.0005)
  GPIO.output(LCD_E, True)
  time.sleep(0.0005)
  GPIO.output(LCD_E, False)
  time.sleep(0.0005)
 
def lcd_string(message,line):
  # Send string to display
 
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def printLCD():
  while True:
    ips = check_output(["hostname", "-I"]).split()[0]
    ip = str(ips)[2:-1]

    lcd_string(f"{ip}" ,LCD_LINE_1)
    time.sleep(1)


def lees_knop(pin):
    global count
    print("button pressed")
    kaas = DataRepository.read_status_actuator_by_id(1)
    if (count == 0):
      print(count)
      count += 1
      time.sleep(0.05)
      lcd_string(f"status: {lcdéén()}",LCD_LINE_2)
    elif (count == 1):
      print(count)
      count += 1
      time.sleep(0.05)
      lcd_string(f"2",LCD_LINE_2)
    elif (count == 2):
      print(count)
      count = 0
      time.sleep(0.05)
      lcd_string(f"3",LCD_LINE_2)

def lcdéén():
  if GPIO.input(relais) == 1:
    return "aan"
  elif GPIO.input(relais) == 0:
    return "uit"


def startIR():
    print("Zoektocht naar IR signalen starten")
    while True:
        print("Wachtend op een signaal")
        GPIO.wait_for_edge(18, GPIO.FALLING)
        code = ir.on_ir_receive(18)
        if code:
            print(str((code)))
            DataRepository.update_waarde_sensor(1,code)
            DataRepository.read_sensor_by_id_one(1)
            DataRepository.read_sensor_by_id_recent(1)
            if (code == 16753245):
                code = 1
                time.sleep(0.75)
                toggle_relais()
                print("code ok")
        else:
            print("Foute code")

def toggle_relais():
    global count
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    count = 0
    if GPIO.input(relais) == 1:
        GPIO.output(relais, GPIO.LOW)
        GPIO.output(groen, GPIO.LOW)
        GPIO.output(rood, GPIO.HIGH)
        DataRepository.update_waarde_actuator(1,formatted_date ,0)
        print("Toggle")
        lcd_string(f"status: {lcdéén()}",LCD_LINE_2)
    else:
        GPIO.output(relais, GPIO.HIGH)
        GPIO.output(groen, GPIO.HIGH)
        GPIO.output(rood, GPIO.LOW)
        DataRepository.update_waarde_actuator(1,formatted_date ,1)
        print("Toggle")
        lcd_string(f"status: {lcdéén()}",LCD_LINE_2)

def socket():
    socketio.run(app, debug=False, host='0.0.0.0')

knop1.on_press(lees_knop)

ir.on_ir_receive()

lcd_init()

proces = threading.Thread(target=printLCD)
proces2 = threading.Thread(target=socket)

if __name__ == '__main__':
  try:
    proces2.start()
    proces.start()
    startIR()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
    
