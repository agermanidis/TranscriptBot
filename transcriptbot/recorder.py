import pyaudio
import sys
import os
import time
import audioop
import math
import contextlib
import array
import multiprocessing
from array import array


@contextlib.contextmanager
def ignore_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)


class Recorder(object):
    def __init__(self,
                 audio_device=0,
                 audio_format=pyaudio.paInt32,
                 rate=44100,
                 chunk_size=4096,
                 pause_threshold_seconds=1.0,
                 include_before_seconds=0.5,
                 include_after_seconds=0.5,
                 add_silence_seconds=0.5,
                 init_energy_threshold=1000000,
                 energy_damping=0.7):
        self.audio_device = audio_device
        self.audio_format = audio_format
        self.rate = rate
        self.chunk_size = chunk_size
        self.session = pyaudio.PyAudio()
        self.sample_width = self.session.get_sample_size(audio_format)
        self.add_silence_seconds = add_silence_seconds
        self.seconds_per_buffer = float(chunk_size)/rate
        self.include_before = include_before_seconds/self.seconds_per_buffer
        self.include_before = int(math.ceil(self.include_before))
        self.include_after = include_after_seconds/self.seconds_per_buffer
        self.include_after = int(math.ceil(self.include_after))
        self.pause_threshold = pause_threshold_seconds/self.seconds_per_buffer
        self.pause_threshold = int(math.ceil(self.pause_threshold))
        self.energy_threshold = init_energy_threshold
        self.energy_damping = energy_damping

    def adjust_threshold(self, sample):
        sample_energy = audioop.rms(sample, self.sample_width)
        self.energy_threshold = self.energy_damping * self.energy_threshold
        self.energy_threshold += (1 - self.energy_damping) * sample_energy

    def add_silence(self, sample):
        n_silence_frames = int(self.add_silence_seconds * self.rate)
        r = array('h', [0 for i in xrange(n_silence_frames)])
        r.extend(sample)
        r.extend([0 for i in xrange(n_silence_frames)])
        return r

    def create_stream(self):
        with ignore_stderr():
            return self.session.open(
                format=self.audio_format,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

    def n_samples(self, duration):
        return int(math.ceil(duration * self.seconds_per_buffer))

    def read_next_chunk(self, stream):
        sample = array('h', stream.read(self.chunk_size))
        if sys.byteorder == 'big':
            sample.byteswap()
        return sample

    def listen_and_adjust_threshold(self, seconds=5):
        stream = self.create_stream()
        for i in range(self.n_samples(seconds)):
            sample = self.read_next_chunk(stream)
            self.adjust_threshold(sample)

    def record_and_enqueue(self, q, debug=False):
        self.listen_and_adjust_threshold()

        stream = self.create_stream()
        current_segment = array('h')
        num_silent = 0
        sound_started = False
        including_after = 0
        previous_segment = None

        try:
            while True:
                sample = self.read_next_chunk(stream)
                current_segment.extend(sample)

                energy = audioop.rms(sample, self.sample_width)
                silent = energy < self.energy_threshold

                self.adjust_threshold(sample)

                if silent:
                    if debug:
                        sys.stdout.write('_')
                        sys.stdout.flush()
                    num_silent += 1
                else:
                    if debug:
                        sys.stdout.write('.')
                        sys.stdout.flush()
                    num_silent = 0
                    sound_started = True

                if previous_segment:
                    previous_segment.extend(sample)
                    including_after += 1
                    if including_after >= self.include_after:
                        previous_segment = self.add_silence(previous_segment)
                        q.put((previous_segment, self.sample_width))
                        previous_segment = None

                if sound_started and num_silent >= self.pause_threshold:
                    if self.include_before:
                        previous_segment = current_segment
                        include_part = current_segment[-self.include_before:]
                        current_segment = array('h', include_part)
                    else:
                        current_segment = array('h', [])
                    including_after = 0
                    num_silent = 0
                    sound_started = False
                    if debug:
                        sys.stdout.write('!')
                        sys.stdout.flush()

        except KeyboardInterrupt:
            self.session.terminate()
