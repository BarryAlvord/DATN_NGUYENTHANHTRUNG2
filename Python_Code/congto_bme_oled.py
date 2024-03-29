import serial
import re
import os
import sys
import smbus
import time
import datetime
from IPython.display import clear_output
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte
from oled.device import ssd1306, sh1106
from oled.render import canvas
from PIL import ImageFont

n = 0
now = datetime.datetime.now()
DEVICE = 0x77 # i2c port of bme280


bus = smbus.SMBus(1)

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
  return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
  # return two bytes from data as an unsigned 16-bit value
  return (data[index+1] << 8) + data[index]

def getChar(data,index):
  # return one byte from data as a signed char
  result = data[index]
  if result > 127:
    result -= 256
  return result

def getUChar(data,index):
  # return one byte from data as an unsigned char
  result =  data[index] & 0xFF
  return result

def readBME280All(addr=DEVICE):
  # Register Addresses
  REG_DATA = 0xF7
  REG_CONTROL = 0xF4
  REG_CONFIG  = 0xF5

  REG_CONTROL_HUM = 0xF2
  REG_HUM_MSB = 0xFD
  REG_HUM_LSB = 0xFE

  # Oversample setting - page 27
  OVERSAMPLE_TEMP = 2
  OVERSAMPLE_PRES = 2
  MODE = 1

  # Oversample setting for humidity register - page 26
  OVERSAMPLE_HUM = 2
  bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

  control = OVERSAMPLE_TEMP<<5 | OVERSAMPLE_PRES<<2 | MODE
  bus.write_byte_data(addr, REG_CONTROL, control)

  # Read blocks of calibration data from EEPROM
  # See Page 22 data sheet
  cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
  cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
  cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

  # Convert byte data to word values
  dig_T1 = getUShort(cal1, 0)
  dig_T2 = getShort(cal1, 2)
  dig_T3 = getShort(cal1, 4)

  dig_P1 = getUShort(cal1, 6)
  dig_P2 = getShort(cal1, 8)
  dig_P3 = getShort(cal1, 10)
  dig_P4 = getShort(cal1, 12)
  dig_P5 = getShort(cal1, 14)
  dig_P6 = getShort(cal1, 16)
  dig_P7 = getShort(cal1, 18)
  dig_P8 = getShort(cal1, 20)
  dig_P9 = getShort(cal1, 22)

  dig_H1 = getUChar(cal2, 0)
  dig_H2 = getShort(cal3, 0)
  dig_H3 = getUChar(cal3, 2)

  dig_H4 = getChar(cal3, 3)
  dig_H4 = (dig_H4 << 24) >> 20
  dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)

  dig_H5 = getChar(cal3, 5)
  dig_H5 = (dig_H5 << 24) >> 20
  dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)

  dig_H6 = getChar(cal3, 6)

  # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
  wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
  time.sleep(wait_time/1000)  # Wait the required time

  # Read temperature/pressure/humidity
  data = bus.read_i2c_block_data(addr, REG_DATA, 8)
  pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
  temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
  hum_raw = (data[6] << 8) | data[7]

  #Refine temperature
  var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
  var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
  t_fine = var1+var2
  temperature = float(((t_fine * 5) + 128) >> 8);

  # Refine pressure and adjust for temperature
  var1 = t_fine / 2.0 - 64000.0
  var2 = var1 * var1 * dig_P6 / 32768.0
  var2 = var2 + var1 * dig_P5 * 2.0
  var2 = var2 / 4.0 + dig_P4 * 65536.0
  var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
  var1 = (1.0 + var1 / 32768.0) * dig_P1
  if var1 == 0:
    pressure=0
  else:
    pressure = 1048576.0 - pres_raw
    pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
    var1 = dig_P9 * pressure * pressure / 2147483648.0
    var2 = pressure * dig_P8 / 32768.0
    pressure = pressure + (var1 + var2 + dig_P7) / 16.0

  # Refine humidity
  humidity = t_fine - 76800.0
  humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
  humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
  if humidity > 100:
    humidity = 100
  elif humidity < 0:
    humidity = 0

  return temperature/100.0,pressure/100.0,humidity
temperature,pressure,humidity = readBME280All()
#left number is x,right number is y(toan toa do)
def stats(oled):
    font = ImageFont.load_default()
    with canvas(oled) as draw:
        draw.text((0, 0), "T: ", font=font, fill=255)
        draw.text((10, 0), str(temperature), font=font, fill=255)
        draw.text((42, 0), "C", font=font, fill=255)
        draw.text((0, 14), "HUM: ", font=font, fill=255)
        draw.text((22, 14), str(humidity), font=font, fill=255)
        draw.text((100, 14), "%", font=font, fill=255)
        draw.text((0, 28), "URMS:", font=font, fill=255)
        draw.text((29, 28), u, font=font, fill=255)
        draw.text((0, 42), "IRMS:", font=font, fill=255)
        draw.text((29, 42), i, font=font, fill=255)
	draw.text((0, 53), "Time:", font=font, fill=255)
        draw.text((29, 53), str(datetime.datetime.now().hour), font=font, fill=255)
        draw.text((41, 53), ":", font=font, fill=255)
        draw.text((47, 53), str(datetime.datetime.now().minute), font=font, fill=255)
port = serial.Serial("/dev/ttyS1", 115200, timeout= 3.0)
def printoled():
    oled = ssd1306(port=0, address=0x3C)
    stats(oled)
while True:
     temperature,pressure,humidity = readBME280All()
     rcv = port.read(24)
     value = (rcv)
     myString = str(value)
            #val = float (value)
            #print (value)

                #val = float (value)
     try:
       u = re.search('Urms:<(.+?)>', value).group(1)
       i = re.search('>Irms:<(.+?)>', value).group(1)
     except AttributeError:
       pass
     printoled()
     if u:
        print "Urms:" + u
     if i:
        print "Irms:" + i
     n = n + 1
     print "Temperature : ", temperature, "C"
     print "Pressure : ", pressure, "hPa"
     print "Humidity : ", humidity, "%"
     print "Current time is :",datetime.datetime.now().hour,":",datetime.datetime.now().minute
     if n > 10:
	n = 0
	os.system("clear")
#	serial.Serial("/dev/ttyS1", 115200).close()
#	print("The port will open again soon")
     else:
	pass
     time.sleep(5)

