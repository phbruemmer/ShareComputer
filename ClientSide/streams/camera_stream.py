import cv2
import threading
from ClientSide.streams import stream_data
import ClientSide.client
CAMERA_STREAM_STOP_EVENT = threading.Event()


def start_camera_stream(sock, activate_new_thread):
    activate_new_thread.set()
    try:
        camera = cv2.VideoCapture(0)

        while not CAMERA_STREAM_STOP_EVENT.is_set() and camera.isOpened():
            ret, frame = camera.read()
            stream_data.send_data(sock, frame)
        camera.release()
    except cv2.error as e:
        print(f"[ERROR] - cv2 error - {e}")
    except Exception as e:
        print(f"[ERROR] - unexpected error - {e}")
