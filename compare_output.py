#!/usr/bin/env python3

import numpy as np
from scipy import signal
import wave
import math
import struct
import matplotlib.pyplot as plt

from gen_synth import flute, note, noise, lowpass, lowpass2, amplitude, note_envelope

comptype="NONE"
compname="not compressed"
nchannels=1
sampwidth=2

notes = [
    ("G4", "notes/g.wav"),
]

def compare_lowpass():
    raw = noise(amplitude(-25))
    a = (1/44100)/((1/44100) + (1/15000))
    filtered = lowpass(a, noise(amplitude(-35)))
    double_filtered = lowpass2(a, noise(amplitude(-35)))

    fig, ax = plt.subplots(1, 3, sharex=True, sharey=True)
    filters = [("Raw", raw), ("1st-order Filtered", filtered), ("2nd-order Filtered", double_filtered)]
    for i, (title, generator) in enumerate(filters):
        sound = np.array([ generator(t / 44100) for t in range(44100) ])
        freqs, times, Sx = signal.spectrogram(sound, fs=44100,
                nperseg=1024, noverlap=24,
                detrend=False, scaling='spectrum')

        ax[i].pcolormesh(times, freqs / 1000, 10 * np.log10(Sx), cmap='plasma',
                vmin=-100,
                vmax=-16)
        if i == 0:
            ax[i].set_ylabel('Frequency (kHz)')
        ax[i].set_xlabel('Time (s)')
        ax[i].set_title(title)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

def compare_bode():
    alpha = 1/1000

    single = signal.lti([1], [alpha, 1])
    double = signal.lti([1], [alpha*alpha, 2*alpha, 1])

    fig, ax = plt.subplots(2, 1, sharex=True, sharey=True)
    for i, (title, system) in enumerate([('First Order', single), ('Second Order', double)]):
        w, mag, _ = signal.bode(system)
        ax[i].set_title(title)
        ax[i].set_xlabel('Frequency (Hz)')
        ax[i].set_ylabel('Gain (dB)')
        ax[i].semilogx(w, mag)
        ax[i].grid()
        ax[i].margins(x=0, y=0)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

def read_wav(filename):
    file = wave.open(filename)
    amplitudes = []
    for _ in range(file.getnframes()):
        data = struct.unpack("<1h", file.readframes(1))
        amplitudes.extend(data)

    # Normalize to -1, 1
    return np.multiply(amplitudes, 1/32768)

def compare_envelope():
    real = np.abs(read_wav("notes/g.wav"))
    real = np.multiply(real, 1/max(real))
        
    generator = note_envelope(len(real)/44100, 1, (0.06, 0.1, 0.65, 0.07))
    synth = np.array([ generator(t / 44100) for t in range(len(real)) ])

    times = [ t / 44100 for t in range(len(real)) ]

    fig, ax = plt.subplots(1, 1)
    ax.plot(times, real)
    ax.plot(times, synth)
    ax.set_ylabel("Amplitude")
    ax.set_xlabel("Time (s)")
    ax.set_title("ADSR Envelope")

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

def compare_note():
    for notename, filename in notes:
        real = read_wav(filename)
        
        generator = flute(note(notename), len(real)/44100)
        synth = np.array([ generator(t / 44100) for t in range(len(real)) ])

        fig, ax = plt.subplots(1, 2, sharex=True, sharey=True)
        for i, (title, sound) in enumerate([("Real", real), ("Synthesized", synth)]):
            freqs, times, Sx = signal.spectrogram(sound, fs=44100,
                    nperseg=1024, noverlap=24,
                    detrend=False, scaling='spectrum')

            # Colormap names: https://matplotlib.org/examples/color/colormaps_reference.html
            ax[i].pcolormesh(times, freqs / 1000, 10 * np.log10(Sx), cmap='plasma',
                    vmin=-100,
                    vmax=-16)
            if i == 0:
                ax[i].set_ylabel('Frequency (kHz)')
            ax[i].set_xlabel('Time (s)')
            ax[i].set_title(title)

        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

# compare_envelope()
# plt.show()

compare_bode()
plt.show()

# compare_lowpass()
# plt.show()

# compare_note()
# plt.show()
