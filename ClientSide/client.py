import logging
import socket
import threading

from ClientSide.streams import camera_stream, mic_stream, screen_stream

PORT = 5000
TIMEOUTS = 10
BUFFER = 1024

AVAILABLE_DEVICES = {'c': [True, 'Cam -> c'],
                     'm': [True, 'Mic -> m'],
                     's': [True, 'Screen -> s']}

ACTIVATE_NEW_THREAD = threading.Event()


def clear_event():
    ACTIVATE_NEW_THREAD.clear()
    print("[threading] event cleared.")


def listen_for_beacon():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    sock.settimeout(TIMEOUTS)

    listening = True
    addr = None

    try:
        while listening:
            print(f"[UDP-info] Listening for beacons on port {PORT}...")
            try:
                data, addr = sock.recvfrom(BUFFER)
                print(f"[UDP-info] Beacon received from {addr}: {data.decode()}")
                continue_listening = input(f"[TCP] > Do you want to connect to {addr}? (y/n)\n")
                if continue_listening == 'y':
                    listening = False
            except socket.timeout:
                listening = False
                print("[timeout] Listening timed out. No beacons received.")
    finally:
        sock.close()
    return addr[0] if addr else None


def client_connected(addr):
    def user_input():
        while True:
            print("[threading] waiting for event...")
            ACTIVATE_NEW_THREAD.wait()
            print("[threading] event received.\n[threading] continuing loop.\n[threading] clearing event...")
            clear_event()
            print("\n# # #\nS E L E C T - O P T I O N\n# # #\n")
            for i in AVAILABLE_DEVICES:
                if AVAILABLE_DEVICES[i][0]:
                    print(AVAILABLE_DEVICES[i][1])
            selected_device = input("(device) > ").lower()
            available = AVAILABLE_DEVICES.get(selected_device, [False])[0]
            if selected_device == 'c' and available:
                AVAILABLE_DEVICES[selected_device][0] = False
                camera_stream_thread = threading.Thread(target=connect, args=(b'c', camera_stream.start_camera_stream))
                camera_stream_thread.start()
            elif selected_device == 'm' and available:
                AVAILABLE_DEVICES[selected_device][0] = False
                mic_stream_thread = threading.Thread(target=connect, args=(b'm', mic_stream.start_mic_stream))
                mic_stream_thread.start()
            elif selected_device == 's' and available:
                AVAILABLE_DEVICES[selected_device][0] = False
                screen_stream_thread = threading.Thread(target=connect, args=(b's', screen_stream.start_screen_stream))
                screen_stream_thread.start()
            elif selected_device == '':
                camera_stream.CAMERA_STREAM_STOP_EVENT.set()
                mic_stream.MIC_INPUT_EVENT.set()
                # SET EVENT -> screen
                main_thread = threading.current_thread()
                for t in threading.enumerate():
                    if t is main_thread:
                        continue
                    logging.debug(f'[threads] joining {t.name}...')
                    t.join()
                exit(0)
            else:
                print("# # #\nI N V A L I D - I N P U T\n# # #")

    def connect(execute_cmd, function):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((addr, PORT))
                print(f'[socket-info] Trying to connect... - {addr}:{PORT}')
                data = sock.recv(BUFFER)
                print(data.decode())
                sock.send(execute_cmd)
                function(sock)
        except socket.error:
            print("[socket-info] Connection error - Is the server running?")
        finally:
            AVAILABLE_DEVICES[execute_cmd.decode()][0] = True

    user_input()


def main():
    addr = listen_for_beacon()
    if addr is None:
        return
    ACTIVATE_NEW_THREAD.set()
    client_connected(addr)


if __name__ == "__main__":
    main()
