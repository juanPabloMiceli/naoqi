#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2022-05-05 02:21:23 (ywatanabe)"

import soundcard as sc
import numpy as np

# get a list of all speakers:
speakers = sc.all_speakers()
# get the current default speaker on your system:
default_speaker = sc.default_speaker()
# get a list of all microphones:
mics = sc.all_microphones()
# get the current default microphone on your system:
default_mic = sc.default_microphone()

print(default_speaker)
print(default_mic)


# record and play back one second of audio:
fs = 48000
rec_sec = 5

data = default_mic.record(samplerate=fs, numframes=fs*rec_sec)
default_speaker.play(data/np.max(data), samplerate=fs)

# alternatively, get a `Recorder` and `Player` object
# and play or record continuously:
with default_mic.recorder(samplerate=fs) as mic, \
      default_speaker.player(samplerate=fs) as sp:
    for _ in range(100):
        data = mic.record(numframes=1024)
        sp.play(data)