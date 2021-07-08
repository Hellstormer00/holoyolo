import socket
import numpy as np
import cv2 as cv

host, port = "0.0.0.0", 9003
DEL = b",\t"
EOM = b"\x04"

def send_pic(img_name):
    img = cv.imread(img_name)
    img = cv.imencode(".png", img)[1].tostring()

    msg = b"GET" + DEL + bytes(str(len(img)), "utf8") + DEL + img
    # print(msg[:40].split(b"\t"))
    s.sendall(msg)

    buf = s.recv(1024).decode("utf8")
    return buf

classes = open('../assets/coco.names').read().strip().split('\n')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))

    print("Horse:\n" + send_pic("horse.jpg"))
    print("Dog:\n" + send_pic("dog.jpg"))

    s.sendall(b"STOP")



