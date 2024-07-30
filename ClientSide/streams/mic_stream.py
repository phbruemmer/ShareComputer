import pyaudio
import socket
import threading
import stream_data


MIC_INPUT_EVENT = threading.Event()
BUFFER = 1024

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=BUFFER)


def start_mic_stream(sock):
    try:
        while not MIC_INPUT_EVENT.is_set():
            mic_inp = stream.read(BUFFER)
            stream_data.send_data(sock, mic_inp)
    except socket.error as e:
        print(f"[ERROR] - Socket error - {e}")
    except Exception as e:
        print(f"[ERROR] - Unexpected error occurred - {e}")

