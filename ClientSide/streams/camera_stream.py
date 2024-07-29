import pickle
import struct
import cv2
import threading

CAMERA_STREAM_STOP_EVENT = threading.Event()


def start_camera_stream(sock):
    camera = cv2.VideoCapture(0)

    while not CAMERA_STREAM_STOP_EVENT.is_set() and camera.isOpened():
        ret, frame = camera.read()
        data_ = pickle.dumps(frame)
        msg = struct.pack("Q", len(data_)) + data_
        sock.send(msg)
    camera.release()
