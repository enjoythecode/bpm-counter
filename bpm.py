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

p = pyaudio.PyAudio()

target_bpm = int(input("enter target BPM"))
target_ms = 60000 / target_bpm

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

print("* recording")

exrms = 0
DELTA_THRESHOLD = 1500
start_ms = current_milli_time()
count = 0
last8 = []
all_bpm = []
all_ms = []
delta_ms = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    data = np.array(wave.struct.unpack("%dh"%(len(data)/WIDTH), data))*2
    
    rms = audioop.rms(data,2)
    if(rms > exrms + DELTA_THRESHOLD):

        count += 1
        now_ms = current_milli_time()
        time_ms = now_ms - start_ms
        last8.append(time_ms)
        all_ms.append(now_ms)
        if(len(all_ms) > 1):
            delta_ms.append(all_ms[-1] - all_ms[-2])

        
        if(len(last8) > 8):
            last8 = last8[1:9]

        print("count", count)
        if(len(last8) == 8):
            print((last8[7] - last8[0]))
            bpm = 7/((last8[7] - last8[0])/1000) * 60
            all_bpm.append(bpm)
            
            print("bpm", all_bpm[-1])
            print("ms diff from target", delta_ms[-1] - target_ms)
            print("ms-bpm", 60000 / delta_ms[-1])


    exrms = rms

print("* done")
stream.stop_stream()
stream.close()

p.terminate()


