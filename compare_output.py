#!/usr/bin/env python3

import numpy as np
from scipy import signal
import wave
import math
import struct
import matplotlib.pyplot as plt

from gen_synth import flute, note, noise, lowpass, lowpass2, lowpass_resonant, amplitude, note_envelope, add, mult, random_wobble, sine, sigmoid, const

comptype="NONE"
compname="not compressed"
nchannels=1
sampwidth=2

notes = [
    # ("G4", "notes/g.wav"),
    ("A#5", "notes/vibrato.wav"),
]

def compare_lowpass():
    raw = noise(amplitude(-25))
    a = (1/44100)/((1/44100) + (1/15000))
    omega = 440 * 2 * 2 * math.pi
    zeta = 0.1
    k = 1
    filtered = lowpass(a, noise(amplitude(-35)))
    double_filtered = lowpass2(a, noise(amplitude(-35)))
    double_filtered2 = lowpass_resonant(k, omega, zeta, noise(amplitude(-35)))

    fig, ax = plt.subplots(1, 4, sharex=True, sharey=True)
    filters = [("Raw", raw), ("1st-order Filtered", filtered), ("2nd-order Filtered", double_filtered), ("2nd-order resonant", double_filtered2)]
    for i, (title, generator) in enumerate(filters):
        sound = np.array([ generator(t / 44100) for t in range(44100) ])
        freqs, times, Sx = signal.spectrogram(sound, fs=44100,
                nperseg=1024, noverlap=24,
                detrend=False, scaling='spectrum')

        ax[i].pcolormesh(times, freqs / (2*math.pi), 10 * np.log10(Sx), cmap='plasma',
                vmin=-100,
                vmax=-16)
        if i == 0:
            ax[i].set_ylabel('Frequency (Hz)')
        ax[i].set_xlabel('Time (s)')
        ax[i].set_title(title)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

def compare_bode():
    alpha = 1/1000
    omega = 440 * 2 * math.pi
    zeta = 0.1
    k = 1

    single = signal.lti([k], [1/omega, 1])
    double = signal.lti([k*omega*omega], [1, 2*omega, omega*omega])
    double2 = signal.lti([k*omega*omega], [1, 2*omega*zeta, omega*omega])

    fig, ax = plt.subplots(3, 1, sharex=True, sharey=True)
    for i, (title, system) in enumerate([('First Order', single), ('Second Order', double), ('Second Order Resonant', double2)]):
        w, mag, _ = signal.bode(system)
        ax[i].set_title(title)
        ax[i].set_xlabel('Frequency (Hz)')
        ax[i].set_ylabel('Gain (dB)')
        ax[i].semilogx(w/(2*math.pi), mag)
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

def compare_modulation():
    vibrato = add(const(0.7), mult(sigmoid(-0.6, scale=30),  sine(5, const(0.6))))
    fluctuation = random_wobble(0.2, 0.8)

    vibrato_synth = np.array([ vibrato(t / 44100) for t in range(44100 * 4) ])
    fluctuation_synth = np.array([ fluctuation(t / 44100) for t in range(44100 * 4) ])

    times = [ t / 44100 for t in range(44100 * 4) ]

    fig, ax = plt.subplots(2, 1, sharex=True, sharey=True)
    ax[0].plot(times, fluctuation_synth)
    ax[1].plot(times, vibrato_synth)
    ax[0].set_ylabel("Amplitude")
    ax[1].set_ylabel("Amplitude")
    ax[1].set_xlabel("Time (s)")
    ax[0].set_title("Fluctuation")
    ax[1].set_title("Brightness Modulation")

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

def compare_note():
    for notename, filename in notes:
        real = read_wav(filename)
        
        generator = flute(note(notename), len(real)/44100, 1)
        synth = np.array([ generator(t / 44100) for t in range(len(real)) ])

        fig, ax = plt.subplots(1, 2, sharex=True, sharey=True)
        for i, (title, sound) in enumerate([("Real", real), ("Synthesized", synth)]):
            freqs, times, Sx = signal.spectrogram(sound, fs=44100,
                    nperseg=1024, noverlap=24,
                    detrend=False, scaling='spectrum')

            # Colormap names: https://matplotlib.org/examples/color/colormaps_reference.html
            ax[i].pcolormesh(times, freqs / (2*math.pi), 10 * np.log10(Sx), cmap='plasma',
                    vmin=-100,
                    vmax=-16)
            if i == 0:
                ax[i].set_ylabel('Frequency (Hz)')
            ax[i].set_xlabel('Time (s)')
            ax[i].set_title(title)

        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

# compare_envelope()
# plt.show()

compare_modulation()
plt.show()

# compare_bode()
# plt.show()

# compare_lowpass()
# plt.show()

compare_note()
plt.show()
