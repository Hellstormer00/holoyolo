import socket
import numpy as np
import cv2 as cv
import time
import numpy as np

host, port = "0.0.0.0", 9003
DEL = b",\t"
EOM = b"\x04"

def timer(name):
    def inner(func):
        def wrapper(*args):
            t1 = time.time()
            out = func(*args)
            t2 = time.time()
            print("Timing for {}: {:.2f} s".format(name, t2 - t1))
            return out
        return wrapper
    return inner


@timer("reading img")
def read_img(img_name):
        img = cv.imread(img_name)
        img = cv.imencode(".png", img)[1].tostring()
        return img

@timer("detecting img")
def send_pic(img):
    msg = b"GET" + DEL + bytes(str(len(img)), "utf8") + DEL + img
    # print(msg[:40].split(b"\t"))
    s.sendall(msg)

    buf = s.recv(1024).decode("utf8")
    return buf

classes = open('../assets/coco.names').read().strip().split('\n')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))

    while True:
        img = read_img("dog.jpg")
        print("Dog:\n" + send_pic(img)) 

    s.sendall(b"STOP")

