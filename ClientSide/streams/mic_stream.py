import struct

import pyaudio
import socket
import threading
from ClientSide.streams import stream_data
import ClientSide.client

MIC_INPUT_EVENT = threading.Event()

BUFFER = 1024


def start_mic_stream(sock):
    p = pyaudio.PyAudio()
    print("[user-input] Select your input device:")
    i = 0
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)['name']
        print(f"[mic-share] {i} : {info}")
    device_index = int(input("Enter device index:\n"))
    if device_index < 0 or device_index > i:
        print(f"[mic-share] couldn't find a device with index {device_index}.")
        sock.send(struct.pack('?', False))
        return

    sock.send(struct.pack('?', True))
    confirmation = struct.unpack('?', sock.recv(1))[0]

    ClientSide.client.ACTIVATE_NEW_THREAD.set()

    if not confirmation:
        print("[mic-share] invalid confirmation code received from server.\nStopping mic-share...")
        return

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=BUFFER)
    try:
        while not MIC_INPUT_EVENT.is_set():
            mic_inp = stream.read(BUFFER)
            stream_data.send_data(sock, mic_inp)
    except socket.error as e:
        print(f"[ERROR] - Socket error - {e}")
    except Exception as e:
        print(f"[ERROR] - Unexpected error occurred - {e}")
    stream.stop_stream()
    stream.close()
    p.terminate()
