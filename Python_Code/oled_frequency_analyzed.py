#Dear maintainer:
#
# For the brave souls who get this far: You are the chosen ones,
# the valiant knights of programming who toil away, without rest,
# fixing our most awful code. To you, true saviors, kings of men,
# I say this: never gonna give you up, never gonna let you down,
# never gonna run around and desert you. Never gonna make you cry,
# never gonna say goodbye. Never gonna tell a lie and hurt you.
#                                                      _Sir barry_2212_
import time
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
RECORD_SECONDS = 5
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
    for el in z : # this will get the locations of each value inside frq into a list
      locations1.append(frq[indexes].tolist().index(el))
    z = np.array(z)
    c = np.amax(Y[indexes][locations1]) # c = max value in Y  aka  the biggest amplitude
    locations = []
     # this will get the locations of the max value inside frq into a list
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
    a =([x for x in frq[indexes] if 50 <= x <= 60]) # Get all the number in the frq array from 50 to 60 and store it in a
    if a:
        locations1, locations, c = check_frequency(a)
        if locations < len(a):
            print "bien do cua quat:"
            print c
            print 'tan so cua quat(Hz):'
            fan_freq = a[locations1][locations]
            print str(fan_freq).strip('[]')
        else:
            print "bien do cua quat:"
            print c
            print 'tan so cua quat(Hz):'
            fan_freq = a[0]
	    print fan_freq
        fan_report = True
    else:
        print "Quat: Off"
        fan_report = False
        fan_freq = 0
    return fan_report, fan_freq
#_______Microwave filter________________________#
def microwave_filter(b):
    b =([x for x in frq[indexes] if 190 <= x <= 210]) # Get all the number in frq array from 190 to 210 and store it in b
    if b:
        locations1, locations, c = check_frequency(b)
        if locations < len(b):
            print "bien do cua lo vi song:"
            print c
            print 'tan so cua lo vi song(Hz):'
            microwave_freq = b[locations1][locations]
            print str(microwave_freq).strip('[]')
        else :
            print "bien do cua lo vi song:"
            print c
            print 'tan so cua lo vi song(Hz):'
            microwave_freq = b[0]
	    print microwave_freq
        microwave_report = True
    else:
        print "Lo vi song: Off"
        microwave_freq = 0
        microwave_report = False
    return microwave_report, microwave_freq
#________________Hairdryer_______________#
def hairdryer_filter(d):
    d =([x for x in frq[indexes] if 890 <= x <= 940]) # Get all the number in the frq array from 890 to 940 and store it in d
    if d:
        locations1, locations, c = check_frequency(d)
        if locations < len(d):
            print "bien do cua may say:"
            print c
            print 'tan so cua may say(Hz):'
            hairdryer_freq = d[locations1][locations]
            print str(hairdryer_freq).strip('[]')
        else :
            print "bien do cua may say:"
            print c
            print 'tan so cua may say(Hz):'
            hairdryer_freq = d[0]
	    print hairdryer_freq
        hairdryer_report = True
    else:
        print "May say: Off"
        hairdryer_freq = 0
        hairdryer_report = False
    return hairdryer_report, hairdryer_freq
#____________________Oled_________________________#
sep = 0
oled = ssd1306(port=0, address=0x3C)
def print_recording():
        font = ImageFont.load_default()
        with canvas(oled) as draw:
            draw.text((0, 0), "Recording....... ", font=font, fill=255)
            logo = Image.open('images/microphone_final.png')
            draw.bitmap((40, 16), logo, fill=1)
def print_status():
#       round up the value in python array then remove the '[]' while print
#                str(np.around(fan_freq, 3)).strip('[]')
#                        ^        ^      ^        ^
#                        |        |      |_       |__________
#                    round up  number      |                |
#                    function  value  number upto        function
#                                      given to         that remove
#                                     be rounded           '[]'
#

	fan_freq1 = str(np.around(fan_freq, 3)).strip('[]')
	microwave_freq1 = str(np.around(microwave_freq, 2)).strip('[]')
 	hairdryer_freq1 = str(np.around(hairdryer_freq, 2)).strip('[]')
        font = ImageFont.load_default()
        with canvas(oled) as draw:
            if fan_report == False:
                draw.text((0, 0), "Fan:Off", font=font, fill=255)
            if fan_report == True:
                draw.text((0, 0), "Fan's freq:", font=font, fill=255)
                draw.text((65, 0), fan_freq1, font=font, fill=255)
            if microwave_report == False:
                draw.text((0, 14), "M.wave:Off", font=font, fill=255)
            if microwave_report == True:
                draw.text((0, 14), "M.wave's freq:", font=font, fill=255)
                draw.text((81, 14), microwave_freq1, font=font, fill=255)
            if hairdryer_report == False:
                draw.text((0, 28), "H.dryer:Off", font=font, fill=255)
            if hairdryer_report == True:
                draw.text((0, 28), "H.dryer's freq:", font=font, fill=255)
                draw.text((85, 28), hairdryer_freq1, font=font, fill=255)
#____________________Loop_________________________#
while True:
    print_recording()
    record()
    frq, Y = audio_data(WAVE_OUTPUT_FILENAME)
    indexes = peakutils.indexes(Y, thres=0.3,min_dist=30) # Get the indexes of the peak in Y array
    fan_report, fan_freq = fan_filter(a)
    microwave_report, microwave_freq = microwave_filter(b)
    hairdryer_report, hairdryer_freq = hairdryer_filter(d)
    print_status()
    time.sleep(5)
