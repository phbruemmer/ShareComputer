import cv2
import sys


def view(video):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    ret, frame = video.read()
    return frame

    # cv2.imshow('frame', frame)


if __name__ == "__main__":
    v = cv2.VideoCapture(0)
    while True:
        view(v)

