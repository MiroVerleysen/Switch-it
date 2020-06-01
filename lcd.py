from repositories.DataRepository import DataRepository
import time
from subprocess import check_output
from helpers.klasseknop import Button
from RPi import GPIO


knop1 = Button(5)
# Definieren LCD pinnen
LCD_RS = 21
LCD_E  = 20
LCD_D4 = 23
LCD_D5 = 26
LCD_D6 = 19
LCD_D7 = 13

# LCD constantes definieren
LCD_WIDTH = 16    # Maximum characters per lijn
LCD_CHR = True
LCD_CMD = False
count = 0
 
LCD_LINE_1 = 0x80 # LCD RAM 1e lijn
LCD_LINE_2 = 0xC0 # LCD RAM 2e lijn

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LCD_E, GPIO.OUT)
GPIO.setup(LCD_RS, GPIO.OUT)
GPIO.setup(LCD_D4, GPIO.OUT)
GPIO.setup(LCD_D5, GPIO.OUT)
GPIO.setup(LCD_D6, GPIO.OUT)
GPIO.setup(LCD_D7, GPIO.OUT)

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
    count += 1
    print(count)
    lcd_string(f"{kaas}",LCD_LINE_2)
  elif (count == 1):
    print("1")
    lcd_string(f"2",LCD_LINE_2)
    count += 1
  elif (count == 2):
    print("3")
    lcd_string(f"3",LCD_LINE_2)
    count = 0

knop1.on_press(lees_knop)

lcd_init()

if __name__ == '__main__':
  try:
    printLCD()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()