import pickle
import socket
import time
import struct
import threading
import cv2
import virtual_cam as vc
import pyvirtualcam

HOST_NAME = socket.gethostname()
HOST = socket.gethostbyname(HOST_NAME)
PORT = 5000
BUFFER = 8192

STOP_EVENT_CONN_HANDLER = threading.Event()
STOP_EVENT_BROADCAST = threading.Event()


def broadcast_beacon():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    msg = "Server Beacon"

    try:
        while not STOP_EVENT_BROADCAST.is_set():
            sock.sendto(msg.encode(), ('<broadcast>', PORT))
            print(f"Broadcast message sent: {msg}")
            time.sleep(5)
    except Exception as e:
        print(f"Broadcasting error: {e}")
    finally:
        sock.close()


def connection_handler():
    def handle_camera_stream():
        print("handle_connection -> Trying to receive camera input")
        data = b''
        payload_size = struct.calcsize("Q")

        print(payload_size)

        with pyvirtualcam.Camera(vc.args.width, vc.args.height, vc.args.fps) as cam:
            print(f'Virtual camera started at {cam.device}')
            while True:
                while len(data) < payload_size:
                    chunk = conn.recv(BUFFER)
                    if not chunk:
                        return
                    data += chunk
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += conn.recv(BUFFER)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame = pickle.loads(frame_data)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cam.send(rgb_frame)
                cam.sleep_until_next_frame()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f" > Listening for connections on {HOST}:{PORT}")

    try:
        while not STOP_EVENT_CONN_HANDLER.is_set():
            sock.settimeout(1)
            try:
                conn, addr = sock.accept()
                print(f"Connection from {addr}")
                STOP_EVENT_BROADCAST.set()
                conn.send(b'Connection successfully established!')
                #
                #   Execute function -> recv. Data e.g. if mic / cam / screen -> execute the corresponding function
                #
                camera_stream_thread = threading.Thread(target=handle_camera_stream)
                camera_stream_thread.start()
            except socket.timeout:
                continue
    except Exception as e:
        print(f"Connection handling error: {e}")
    finally:
        sock.close()


def main():
    broadcast_thread = threading.Thread(target=broadcast_beacon)
    broadcast_thread.start()

    connection_thread = threading.Thread(target=connection_handler)
    connection_thread.start()

    try:
        while not STOP_EVENT_CONN_HANDLER.is_set() or not STOP_EVENT_BROADCAST.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
        STOP_EVENT_BROADCAST.set()
        STOP_EVENT_CONN_HANDLER.set()
        broadcast_thread.join()
        connection_thread.join()
        print("Server stopped.")


if __name__ == '__main__':
    main()
