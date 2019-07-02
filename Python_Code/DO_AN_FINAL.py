# Never Been tested befor
import serial
import re
import os
import sys
import smbus
import time
import datetime
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte
from IPython.display import clear_output
from oled.device import ssd1306, sh1106
from oled.render import canvas
from PIL import ImageFont
import pyowm
import scipy
from scipy import fft, arange
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import os
import peakutils
count = 0
#_____________________BME_______________________________#
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

#______________________WEATHER's DATA___________________________#
owm = pyowm.OWM('df011d755a92d9f16ce98ff71d0292f2')  # You MUST provide a valid API key
observation = owm.weather_at_place('Hanoi,VN') #weather of your location
def weather():

    # owm = pyowm.OWM(API_key='your-API-key', subscription_type='pro') # pro subscription

    # Search for current weather in Your city
    w = observation.get_weather() #weather status
    #print(w)

    # Weather details
    w.get_humidity()              #Humidity
    print (w.get_temperature('celsius')['temp'])#print temp-celsius

    return w.get_temperature('celsius')['temp']
#_________________Frequency_analyzed_____________________#
def frequency_sepectrum(x, sf):
    """
    Derive frequency spectrum of a signal from time domain
    :param x: signal in the time domain
    :param sf: sampling frequency
    :returns frequencies and their content distribution
    """
    x = x - np.average(x)  # zero-centering

    n = len(x)
    k = arange(n)
    tarr = n / float(sf)
    frqarr = k / float(tarr)  # two sides frequency range

    frqarr = frqarr[range(n // 2)]  # one side frequency range

    x = fft(x) / n  # fft computing and normalization
    x = x[range(n // 2)]

    return frqarr, abs(x)


def check_frequency(z):
    locations1 = []
    for el in z : # this will get the locations inside frq into a list
      locations1.append(frq[indexes].tolist().index(el))
    z = np.array(z)
    c = np.amax(Y[indexes][locations1])
    locations = []
     # this will get the locations inside frq into a list
    locations.append(Y[indexes].tolist().index(c))
    k = locations
    return np.any(locations1), np.any(locations), c

#_______________read audio file's data_________________#
def audio_data(WAVE_OUTPUT_FILENAME):
    here_path = os.path.dirname(os.path.realpath(__file__))
    wav_file_name = WAVE_OUTPUT_FILENAME
    wave_file_path = os.path.join(here_path, wav_file_name)
    sr, signal = wavfile.read(wave_file_path)

    y = signal[:, 0]  # use the first channel (or take their average, alternatively)

    frq, Y = frequency_sepectrum(y, sr)
    return frq, Y


#_____________________________audio define_____________________#
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "test10.wav"
a = []
b = []
d = []

#___________________________Record_____________________________#
def record():
    audio = pyaudio.PyAudio()
    os.system("clear")
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    print "recording..."
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    print "finished recording"


    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()


#__________________fan filter____________________#
def fan_filter(a):
    a =([x for x in frq[indexes] if 40 <= x <= 60]) # creat a: where store the array value from 40 to 60 that cut from the the frequency array
    if a:
        locations1, locations, c = check_frequency(a)
        if locations < len(a):
            print "bien do cua quat:"
            print c
            print 'tan so cua quat(Hz):'
            fan_freq = a[locations1][locations]
            print fan_freq
        else:
            print "bien do cua quat:"
            print c
            print 'tan so cua quat(Hz):'
            print a
            fan_freq = a

        fan_report = True
    else:
        print "Quat: Off"
        fan_report = False
        fan_freq = 0
    return fan_report, fan_freq

#_________________Microwave filter________________________#
def microwave_filter(b):
    b =([x for x in frq[indexes] if 150 <= x <= 170]) # creat b: where store the array value from 150 to 170 that cut from the the frequency array
    if b:
        locations1, locations, c = check_frequency(b)
        if locations < len(b):
            print "bien do cua lo vi song:"
            print c
            print 'tan so cua lo vi song(Hz):'
            microwave_freq = b[locations1][locations]
            print microwave_freq[0]
        else :
            print "bien do cua lo vi song:"
            print c
            print 'tan so cua lo vi song(Hz):'
            print b[0]
            microwave_freq = b[0]
        microwave_report = True
    else:
        print "Lo vi song: Off"
        microwave_freq = 0
        microwave_report = False
    return microwave_report, microwave_freq

#___________________Hairdryer filter_______________#
def hairdryer_filter(d):
    d =([x for x in frq[indexes] if 95 <= x <= 110]) #creat d: where store the array value from 95 to 110 that cut from the the frequency array
    if d:
        locations1, locations, c = check_frequency(d)
        if locations < len(d):
            print "bien do cua may say:"
            print c
            print 'tan so cua may say(Hz):'
            hairdryer_freq = d[locations1][locations]
            print hairdryer_freq[0]
        else :
            print "bien do cua may say:"
            print c
            print 'tan so cua may say(Hz):'
            print d[0]
            hairdryer_freq = d[0]
        hairdryer_report = True
    else:
        print "May say: Off"
        hairdryer_freq = 0
        hairdryer_report = False
    return hairdryer_report, hairdryer_freq

#____________________Oled_________________________#
oled = ssd1306(port=0, address=0x3C)
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
def print_recording():
        font = ImageFont.load_default()
        with canvas(oled) as draw:
            draw.text((0, 0), "Recording....... ", font=font, fill=255)
            logo = Image.open('images/microphone_final.png')
            draw.bitmap((40, 16), logo, fill=1)
def print_status():
        font = ImageFont.load_default()
        with canvas(oled) as draw:
            if fan_report == False:
                draw.text((0, 0), "Quat: Off", font=font, fill=255)
            if fan_report == True:
                draw.text((0, 0), "Quat's freq:", font=font, fill=255)
                draw.text((100, 0), str(fan_freq), font=font, fill=255)
            if microwave_report == False:
                draw.text((0, 14), "Lo vi song : Off", font=font, fill=255)
            if microwave_report == True:
                draw.text((0, 14), "Lo Vi song's freq:", font=font, fill=255)
                draw.text((22, 14), str(microwave_freq), font=font, fill=255)
            if hairdryer_report == False:
                draw.text((0, 28), "May Say: Off", font=font, fill=255)
            if hairdryer_report == True:
                draw.text((0, 28), "May Say's freq:", font=font, fill=255)
                draw.text((29, 28),str(hairdryer_freq), font=font, fill=255)
#____________________Loop_________________________#
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
     stats(oled)
     if u:
        print "Urms:" + u
     if i:
        print "Irms:" + i
     n = n + 1
     print "Temperature : ", temperature, "C"
     print "Pressure : ", pressure, "hPa"
     print "Humidity : ", humidity, "%"
     print "We start at 14:10"
     print "Current time is :",datetime.datetime.now().hour,":",datetime.datetime.now().minute
     time.sleep(5)
    record()
    frq, Y = audio_data(WAVE_OUTPUT_FILENAME)
    indexes = peakutils.indexes(Y) #find peak of the frequency to minimize the frequency array
    fan_report, fan_freq = fan_filter(a)
    microwave_report, microwave_freq = microwave_filter(b)
    hairdryer_report, hairdryer_freq = hairdryer_filter(d)
    print_status()
    if count > 10:
        count = 0
        os.system("clear")
    else:
        pass
    time.sleep(5)
