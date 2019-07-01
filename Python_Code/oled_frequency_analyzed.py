import time
import matplotlib.pyplot as plt
import scipy
from scipy import fft, arange
import os
import pyaudio
import wave
from scipy.io import wavfile
import numpy as np
import peakutils
from IPython.display import clear_output
from demo_opts import device
from oled.render import canvas
from PIL import Image
from oled.device import ssd1306, sh1106
from oled.render import canvas
from PIL import ImageFont

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
#___________________________________________________________#

#_______________read audio file's data_________________#
def audio_data(WAVE_OUTPUT_FILENAME):
    here_path = os.path.dirname(os.path.realpath(__file__))
    wav_file_name = WAVE_OUTPUT_FILENAME
    wave_file_path = os.path.join(here_path, wav_file_name)
    sr, signal = wavfile.read(wave_file_path)

    y = signal[:, 0]  # use the first channel (or take their average, alternatively)

    frq, Y = frequency_sepectrum(y, sr)
    return frq, Y
#_____________________________________________________#

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
#______________________________________________________________#

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
#________________________________________________________#

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
    print Y[indexes][locations1]
    c = np.amax(Y[indexes][locations1])
    locations = []
     # this will get the locations inside frq into a list
    locations.append(Y[indexes].tolist().index(c))
    k = locations
    return np.any(locations1), np.any(locations), c
#___________________________________________________________#

#_______________read audio file's data_________________#
def audio_data(WAVE_OUTPUT_FILENAME):
    here_path = os.path.dirname(os.path.realpath(__file__))
    wav_file_name = WAVE_OUTPUT_FILENAME
    wave_file_path = os.path.join(here_path, wav_file_name)
    sr, signal = wavfile.read(wave_file_path)

    y = signal[:, 0]  # use the first channel (or take their average, alternatively)

    frq, Y = frequency_sepectrum(y, sr)
    return frq, Y
#_____________________________________________________#
#___________________________#
#________fan filter____________________#
def fan_filter(a):
    a =([x for x in frq[indexes] if 40 <= x <= 60])
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
#_______Microwave filter________________________#
def microwave_filter(b):
    b =([x for x in frq[indexes] if 150 <= x <= 170])
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
#________________Hairdryer_______________#
def hairdryer_filter(d):
    d =([x for x in frq[indexes] if 95 <= x <= 110])
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
    record()
    frq, Y = audio_data(WAVE_OUTPUT_FILENAME)
    indexes = peakutils.indexes(Y)
    fan_report, fan_freq = fan_filter(a)
    microwave_report, microwave_freq = microwave_filter(b)
    hairdryer_report, hairdryer_freq = hairdryer_filter(d)
    print_status()
    time.sleep(5)
