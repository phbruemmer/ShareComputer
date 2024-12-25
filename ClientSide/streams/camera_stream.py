import cv2
import threading
import numpy as np
from . import stream_data

CAMERA_STREAM_STOP_EVENT = threading.Event()


def start_camera_stream(sock, activate_new_thread):
    activate_new_thread.set()
    try:
        camera = cv2.VideoCapture(0)

        while not CAMERA_STREAM_STOP_EVENT.is_set() and camera.isOpened():
            ret, frame = camera.read()
            if not ret:
                break

            # Compress the frame
            encode_param = [cv2.IMWRITE_JPEG_QUALITY, 50]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)

            stream_error_report = stream_data.send_data(sock, buffer.tobytes())
            if stream_error_report:
                CAMERA_STREAM_STOP_EVENT.set()
        camera.release()
    except cv2.error as e:
        print(f"[ERROR] - cv2 error - {e}")
    except Exception as e:
        print(f"[ERROR] - unexpected error - {e}")
