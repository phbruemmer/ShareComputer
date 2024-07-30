import socket
import pickle
import struct


def send_data(sock, data):
    try:
        data_ = pickle.dumps(data)
        msg = struct.pack('Q', len(data_)) + data_
        sock.send(msg)
    except socket.error as e:
        print(f"[ERROR] - socket error - {e}")
    except Exception as e:
        print(f"[ERROR] - unexpected error - {e}")
