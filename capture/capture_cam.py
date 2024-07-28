import cv2
import sys


def view(video):
    ret, frame = video.read()
    return frame

    # cv2.imshow('frame', frame)


if __name__ == "__main__":
    v = cv2.VideoCapture(0)
    while True:
        view(v)

