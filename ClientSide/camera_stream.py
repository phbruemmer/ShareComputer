import pickle
import struct
import cv2
from capture import capture_cam
import threading

CAMERA_STREAM_STOP_EVENT = threading.Event()


def start_camera_stream(sock):
    camera = cv2.VideoCapture(0)
    resolution_x = capture_cam.view(camera).shape[0]
    resolution_y = capture_cam.view(camera).shape[1]
    print(resolution_x)
    print(resolution_y)
    sock.send(pickle.dumps([resolution_x, resolution_y]))

    while not CAMERA_STREAM_STOP_EVENT.is_set():
        frame = capture_cam.view(camera)
        data_ = pickle.dumps(frame)
        msg = struct.pack("Q", len(data_)) + data_
        sock.send(msg)
