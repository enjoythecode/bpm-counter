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
RECORD_SECONDS = 1000

RMS_DELTA_THRESHOLD = 1500
SLIDING_TIMESTAMP_LENGTH = 8

p = pyaudio.PyAudio()

target_bpm = int(input("enter target BPM: "))
target_ms = 60000 / target_bpm

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

print("* recording")

past_rms = 0
beat_count = 0
sliding_timestamps = []

all_bpm = []
all_timestamps = []
all_delta = []

start_ms = current_milli_time()

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    data = np.array(wave.struct.unpack("%dh"%(len(data)/WIDTH), data))*2
    
    curr_rms = audioop.rms(data,2)
    if(curr_rms > past_rms + RMS_DELTA_THRESHOLD):

        beat_count += 1
        now_ms = current_milli_time()
        time_ms = now_ms - start_ms
        sliding_timestamps.append(time_ms)
        all_timestamps.append(now_ms)
        if(len(all_timestamps) > 1):
            all_delta.append(all_timestamps[-1] - all_timestamps[-2])

        if(len(sliding_timestamps) > SLIDING_TIMESTAMP_LENGTH):
            sliding_timestamps = sliding_timestamps[1:SLIDING_TIMESTAMP_LENGTH+1]

        print("*"*10)
        print("beat_count", beat_count)
        if(len(sliding_timestamps) == SLIDING_TIMESTAMP_LENGTH):
            print(all_delta[-1])
            bpm = (SLIDING_TIMESTAMP_LENGTH - 1)/((sliding_timestamps[SLIDING_TIMESTAMP_LENGTH - 1] - sliding_timestamps[0])/1000) * 60
            all_bpm.append(bpm)
            
            print("bpm over last " + str(SLIDING_TIMESTAMP_LENGTH) + "beats: " , all_bpm[-1])
            print("ms diff from target: ", all_delta[-1] - target_ms)
            print("ms-bpm: ", 60000 / all_delta[-1])


    past_rms = curr_rms

print("* done")
stream.stop_stream()
stream.close()

p.terminate()


