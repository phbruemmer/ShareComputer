import socket
import time
import threading

HOST_NAME = socket.gethostname()
HOST = socket.gethostbyname(HOST_NAME)
PORT = 5000

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
                conn.close()
                STOP_EVENT_CONN_HANDLER.set()
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
