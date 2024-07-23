import socket

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
                listening = False
            except socket.timeout:
                listening = False
                print("Listening timed out. No beacons received.")
    finally:
        sock.close()
    return addr[0]


def client_connected(sock):
    data = sock.recv(BUFFER)
    print(data.decode())


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
