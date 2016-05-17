import json
import os
import requests
import struct
import subprocess
import tempfile
import tempfile
import wave
from datetime import datetime

GOOGLE_SPEECH_API_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
GOOGLE_SPEECH_API_URL = "http://www.google.com/speech-api/v2/recognize" + \
                        "?client=chromium&lang={lang}&key={key}"


def speech_api_call(data,
                    language="en-US",
                    rate=16000,
                    retries=3,
                    api_key=GOOGLE_SPEECH_API_KEY):
    for i in range(retries):
        url = GOOGLE_SPEECH_API_URL.format(lang=language, key=api_key)
        headers = {"Content-Type": "audio/x-flac; rate=%d" % rate}

        try:
            resp = requests.post(url, data=data, headers=headers)
        except requests.exceptions.ConnectionError:
            continue

        for line in resp.content.split("\n"):
            try:
                line = json.loads(line)
                transcript = line['result'][0]['alternative'][0]['transcript']
                return transcript.capitalize()
            except:
                continue


def wav2flac(source_path):
    temp = tempfile.NamedTemporaryFile(suffix='.flac')
    command = ["ffmpeg", "-y", "-i", source_path,
               "-ac", "1", "-ar", "16000",
               "-loglevel", "error", temp.name]
    subprocess.check_output(command)
    return temp.read()


def write_wav(frames, sample_width, rate=16000, channels=1):
    data = struct.pack('<' + ('h'*len(frames)), *frames)
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    wf = wave.open(tmp.name, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(rate)
    wf.writeframes(data)
    wf.close()
    return tmp.name


def transcribe(data, sample_width, rate):
    filename = write_wav(data, sample_width, rate=rate)
    flac_data = wav2flac(filename)
    transcript = speech_api_call(flac_data)
    os.remove(filename)
    return transcript


def transcriber_thread(in_q, out_q, rate=44100):
    try:
        while True:
            frames, width = in_q.get()
            result = transcribe(frames, width, rate)
            if result:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print('[{0}] {1}'.format(timestamp, result))
                out_q.put(result)
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
