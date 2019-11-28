# Author: Sinan Yumurtaci -- sinan@enjoythecode.com
# Date: 11/27/2019
# Purpose: "Calculate" BPM from microphone by detecting sudden rises in sound loudness and registering the time between each "beat."
# 
# Useful making sure you aren't going too fast/slow.
# Works best with BPM < 300, and in quiet environments. Can tolerate constant noise for the most part (e.g. fan)
#
# Complimentary to my drumming hobby. Enjoy!

import pyaudio
import numpy as np
import wave
import audioop
import time
import matplotlib.pyplot as plt

current_milli_time = lambda: int(round(time.time() * 1000))

CHUNK = 1024
WIDTH = 2
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 1000 # the program runs for this many seconds. set to a high number for indefinite sessions

RMS_DELTA_THRESHOLD = 5 # how much of a change in sound registers as a beat. Higher values are more insensitive and vice versa
SLIDING_TIMESTAMP_LENGTH = 8 # calculates BPM using last SLIDING_TIMESTAMP_LENGTH beats

p = pyaudio.PyAudio()

target_bpm = int(input("enter target BPM: "))
target_ms = 60000 / target_bpm

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)


past_rms = 0
beat_count = 0
sliding_timestamps = []

all_bpm = []
all_timestamps = []
all_delta = []

start_ms = current_milli_time()

print("***** == RECORDING == *****")

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    data = np.array(wave.struct.unpack("%dh"%(len(data)/WIDTH), data))*2
    
    curr_rms = audioop.rms(data,2)

    # is there a beat?
    if(curr_rms > max(past_rms, 400) * RMS_DELTA_THRESHOLD):

        beat_count += 1
        now_ms = current_milli_time()
        time_ms = now_ms - start_ms
        sliding_timestamps.append(time_ms)
        all_timestamps.append(now_ms)

        # start calculating "delta" (time between beats) from the second beat on
        if(len(all_timestamps) > 1):
            all_delta.append(all_timestamps[-1] - all_timestamps[-2])

        # ensure the sliding timestamps array is not too long
        if(len(sliding_timestamps) > SLIDING_TIMESTAMP_LENGTH):
            sliding_timestamps = sliding_timestamps[1:SLIDING_TIMESTAMP_LENGTH+1]

        print("*"*10)
        print("beat #", beat_count)
        if(len(sliding_timestamps) == SLIDING_TIMESTAMP_LENGTH):
            print(all_delta[-1])
            bpm = (SLIDING_TIMESTAMP_LENGTH - 1)/((sliding_timestamps[SLIDING_TIMESTAMP_LENGTH - 1] - sliding_timestamps[0])/1000) * 60
            all_bpm.append(bpm)
            
            print("BPM over last " + str(SLIDING_TIMESTAMP_LENGTH) + " beats: " , all_bpm[-1])
            print("millisecond difference from target: ", all_delta[-1] - target_ms)
            print("BPM @ last millisecond delay: ", 60000 / all_delta[-1])


    past_rms = curr_rms

print("***** == DONE == *****")

stream.stop_stream()
stream.close()
p.terminate()