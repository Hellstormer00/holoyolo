import socket
import numpy as np
import cv2 as cv

host, port = "0.0.0.0", 9001
DEL = b",\t"
EOM = b"\x04"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))

    img = cv.imread("horse.jpg")
    img = cv.imencode(".png", img)[1].tostring()

    msg = b"GET" + DEL + bytes(str(len(img)), "utf8") + DEL + img + EOM
    print(msg[:40].split(b"\t"))
    s.sendall(msg)

    buf = s.recv(1024).decode("utf8")
    print(buf)



    