# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from helpers.klasseIR import InfraRood
from datetime import datetime

from time import time
import threading

# Code voor led
from helpers.klasseknop import Button
from RPi import GPIO


led1 = 6
rood = 22
groen = 27
knop1 = Button(5)
ir = InfraRood(18)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(rood, GPIO.OUT)
GPIO.setup(groen, GPIO.OUT)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

@app.route('/read_all')
def ophalen_sensor_data():
    output = DataRepository.read_all_sensors()
    return jsonify(data = output), 200

@app.route('/read_actuator/<actuatorID>')
def ophalen_actuator_data(actuatorID):
    output = DataRepository.read_status_actuator_by_id(actuatorID)
    return jsonify(data = output), 200

def lees_knop(pin):
    print("button pressed")
    toggle_relais()
    

def startIR():
    print("Zoektocht naar IR signalen starten")
    while True:
        print("Wachtend op een signaal")
        GPIO.wait_for_edge(18, GPIO.FALLING)
        code = ir.on_ir_receive(18)
        if code:
            print(str(code))
            DataRepository.update_waarde_sensor(1,code)
            if (str(hex(code)) == "0xffa25d"):
                print("Toggle")
                toggle_relais()
        else:
            print("Foute code")

def toggle_relais():
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    if GPIO.input(led1) == 1:
        GPIO.output(led1, GPIO.LOW)
        GPIO.output(groen, GPIO.LOW)
        GPIO.output(rood, GPIO.HIGH)
        DataRepository.update_waarde_actuator(1,formatted_date ,0)
    else:
        GPIO.output(led1, GPIO.HIGH)
        GPIO.output(groen, GPIO.HIGH)
        GPIO.output(rood, GPIO.LOW)
        DataRepository.update_waarde_actuator(1,formatted_date ,1)


def socket():
    socketio.run(app, debug=False, host='0.0.0.0')

knop1.on_press(lees_knop)

ir.on_ir_receive()

proces = threading.Thread(target=socket)


if __name__ == '__main__':
    proces.start()
    startIR()