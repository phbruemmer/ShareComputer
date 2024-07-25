import argparse
import cv2

parser = argparse.ArgumentParser(description='Stream video from a camera to a virtual camera.')
parser.add_argument('--camera_index', type=int, default=0, help='Index of the physical camera.')
parser.add_argument('--width', type=int, default=640, help='Width of the video frame.')
parser.add_argument('--height', type=int, default=480, help='Height of the video frame.')
parser.add_argument('--fps', type=int, default=30, help='Frames per second.')

args = parser.parse_args()

cap = cv2.VideoCapture(args.camera_index)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)