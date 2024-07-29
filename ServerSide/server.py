import pickle
import socket
import time
import struct
import threading
import cv2
import pyvirtualcam

HOST_NAME = socket.gethostname()
HOST = socket.gethostbyname(HOST_NAME)
PORT = 5000
BUFFER = 8192

STOP_EVENT_CONN_HANDLER = threading.Event()
STOP_EVENT_BROADCAST = threading.Event()

AVAILABLE_DEVICES = {b'c': True,
                     b'm': True,
                     b's': True}


def broadcast_beacon():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    msg = "Server Beacon"

    try:
        while not STOP_EVENT_BROADCAST.is_set():
            sock.sendto(msg.encode(), ('<broadcast>', PORT))
            print(f"[broadcast] Broadcast message sent: {msg}")
            time.sleep(5)
    except Exception as e:
        print(f"[ERROR] Broadcasting error: {e}")
    finally:
        sock.close()


def connection_handler(conn, addr):
    def cmd_handler():
        recv_cmd = conn.recv(BUFFER)
        if recv_cmd in AVAILABLE_DEVICES and AVAILABLE_DEVICES[recv_cmd]:
            if recv_cmd == b'c':
                AVAILABLE_DEVICES[recv_cmd] = False
                try:
                    handle_camera_stream()
                finally:
                    AVAILABLE_DEVICES[recv_cmd] = True
            elif recv_cmd == b'm':
                AVAILABLE_DEVICES[recv_cmd] = False
                try:
                    handle_mic_stream()
                finally:
                    AVAILABLE_DEVICES[recv_cmd] = True
            elif recv_cmd == b's':
                AVAILABLE_DEVICES[recv_cmd] = False
                try:
                    handle_screen_stream()
                finally:
                    AVAILABLE_DEVICES[recv_cmd] = True

    def handle_camera_stream():
        print(f"[cam-share] handle_camera_stream -> Connection from {addr}")
        data = b''
        payload_size = struct.calcsize("Q")

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
        res_y, res_x = frame.shape[:2]

        with pyvirtualcam.Camera(width=res_x, height=res_y, fps=30) as cam:
            print(f'[cam-share] Virtual camera started at {cam.device} with resolution {res_x}x{res_y}')
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

    def handle_screen_stream():
        print(f"[screen-share] handle_screen_stream -> Connection from {addr}")

    def handle_mic_stream():
        print(f"[mic-share] handle_mic_stream -> Connection from {addr}")

    try:
        conn.send(b'Connection successfully established!')
        cmd_handler()
    except Exception as e:
        print(f"[ERROR] Error in connection handler for {addr}: {e}")
    finally:
        conn.close()
        print(f"[socket-info] Connection with {addr} closed")


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"TCP-info > Listening for connections on {HOST}:{PORT}")

    try:
        while not STOP_EVENT_CONN_HANDLER.is_set():
            sock.settimeout(1)
            try:
                conn, addr = sock.accept()
                if not STOP_EVENT_BROADCAST.is_set():
                    STOP_EVENT_BROADCAST.set()
                print(f"[socket-info] Connection from {addr}")
                connection_handler_thread = threading.Thread(target=connection_handler, args=(conn, addr))
                connection_handler_thread.start()
            except socket.timeout:
                continue
    except Exception as e:
        print(f"[ERROR] Connection handling error: {e}")
    finally:
        sock.close()
        print("[socket-info] Server socket closed")


def main():
    broadcast_thread = threading.Thread(target=broadcast_beacon)
    broadcast_thread.start()

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[socket-info] Stopping server...")
        STOP_EVENT_BROADCAST.set()
        STOP_EVENT_CONN_HANDLER.set()
        broadcast_thread.join()
        server_thread.join()
        print("[socket-info] Server stopped.")


if __name__ == '__main__':
    main()
