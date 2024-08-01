import struct

import cv2
import numpy as np
import mss
import mss.tools
import threading

SCREEN_STREAM_EVENT = threading.Event()


def start_screen_stream(sock, activate_new_thread):
    with mss.mss() as sct:
        print("[screen-share] Select your monitor:")
        i = 0
        for i, monitor_ in enumerate(sct.monitors):
            print(f"[screen-share] {i} : {monitor_}")
        monitor_index = int(input("Enter monitor index:"))
        if monitor_index < 0 or monitor_index > i:
            print("[screen-share] invalid monitor index.\n[screen-share] returning...")
            sock.send(struct.pack('?', False))
            return
        sock.send(struct.pack('?', True))
        activate_new_thread.set()
        confirmation = struct.unpack('?', sock.recv(1))[0]
        if not confirmation:
            return
        monitor = sct.monitors[monitor_index]

        while not SCREEN_STREAM_EVENT.is_set():
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imshow('Rec', frame)
