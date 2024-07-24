import socket
import threading

import camera_stream

PORT = 5000

TIMEOUTS = 10
BUFFER = 1024


def listen_for_beacon():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    sock.settimeout(TIMEOUTS)

    listening = True
    addr = None

    try:
        while listening:
            print(f"Listening for (UDP-) beacons on port {PORT}...")
            try:
                data, addr = sock.recvfrom(BUFFER)
                print(f"Beacon received from {addr}: {data.decode()}")
                continue_listening = input(f" > Do you want to connect to {addr}? (y/n)\n")
                if continue_listening == 'y':
                    listening = False
            except socket.timeout:
                listening = False
                print("Listening timed out. No beacons received.")
    finally:
        sock.close()
    return addr[0]


def client_connected(sock):
    def user_input():
        print("# # #\nS E L E C T - O P T I O N\n# # #\nCam -> c\nMic -> m\nScreen -> s\n")
        selected_device = input("(device) > ").lower()
        if selected_device == 'c':
            camera_thread = threading.Thread(target=camera_stream.start_camera_stream, args=(sock,))
            camera_thread.start()
        elif selected_device == 'm':
            pass
        elif selected_device == 's':
            pass
        elif selected_device == '':
            camera_stream.CAMERA_STREAM_STOP_EVENT.set()
            sock.close()
            exit(0)
        else:
            print("# # #\nI N V A L I D - I N P U T\n# # #")
        return False
    data = sock.recv(BUFFER)
    print(data.decode())
    #
    #   CONTINUE HERE -> User input - mic / cam / screen -> send data to the server... (basic Idea)
    #
    while not user_input():
        user_input()


def TCP_connect(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((addr, PORT))
        print(f'Successfully connected to the Server. {addr}:{PORT}')
        client_connected(sock)
    except socket.error:
        print("Connection error - Is the server running?")
    except KeyboardInterrupt:
        sock.close()


def main():
    addr = listen_for_beacon()
    if addr is None:
        return
    TCP_connect(addr)


if __name__ == "__main__":
    main()