import socket
import cv2 as cv
import numpy as np

host, port = '172.22.223.57', 9001

def recv_all(size, conn):
    buf = b""
    while len(buf) < size:
        packet = conn.recv(size - len(buf))
        print(size - len(buf))
        buf += packet
        print(f"received {len(packet)} bytes")
        if not packet:
            return None
    return buf

def img_processing(img_bin):
    img_bin = np.array([el for el in img_bin], dtype="uint8")
    return cv.imdecode(img_bin, cv.IMREAD_UNCHANGED)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    print("server initialized")
    print("listening on port", port)
    while True:
        conn, addr = s.accept()
        print(f"connected to {addr}")

        with conn:
            img_size = int(conn.recv(1024))
            print(f"receiving {img_size} bytes")

            img = recv_all(img_size, conn)
            print("data:", img[0:20], "...")
            img = img_processing(img)
            cv.imshow("Yaaaay", img)
            cv.waitKey(0)

            conn.send(b"OK\n")
            print("closing connection")
    
