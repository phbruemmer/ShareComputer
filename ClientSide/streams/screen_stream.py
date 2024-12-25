import struct
import cv2
import numpy as np
import mss
import mss.tools
import threading
import stream_data

SCREEN_STREAM_EVENT = threading.Event()
STD_RESOLUTION = (1920, 1080)


def start_screen_stream(sock, activate_new_thread):
    with mss.mss() as sct:
        print("[screen-share] Select your monitor:")
        i = 0
        for i, monitor_ in enumerate(sct.monitors):
            print(f"[screen-share] {i} : {monitor_}")
        monitor_index = int(input("Enter monitor index:"))
        activate_new_thread.set()
        if monitor_index < 0 or monitor_index > i:
            print("[screen-share] invalid monitor index.\n[screen-share] returning...")
            sock.send(struct.pack('?', False))
            return
        sock.send(struct.pack('?', True))
        monitor = sct.monitors[monitor_index]
        try:
            while not SCREEN_STREAM_EVENT.is_set():
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, STD_RESOLUTION, interpolation=cv2.INTER_AREA)
                stream_error_report = stream_data.send_data(sock, frame)
                if stream_error_report:
                    SCREEN_STREAM_EVENT.set()
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            cv2.destroyAllWindows()
            print("[screen-share] Cleaned up.\n[screen-share] exiting...")
