import socket
import cv2 as cv
import numpy as np
import detection
import re

host, port = '0.0.0.0', 9003
MIN_CONF = 0.9
DEL = b",\t"
EOM = b"\x04"

def recv_all(size, conn, part):
    buf = part
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


def recv_img(conn):
    # format: GET imgsize img\x04
    cmd, img_size, img_part = conn.recv(1024).split(DEL)
    img_size = int(img_size)
    print(f"receiving {img_size} bytes")
    img = recv_all(img_size, conn, img_part)
    print("data:", img[0:20], "...")
    return img


def init_socket(host, port, s):
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    print("server initialized")
    print("listening on port", port)


def send_outputs(pred, conn, classes):
    out = ""
    for output in pred:
        out += "{0}{3}{1}{3}{2}\n".format(output[0], classes[output[1]], output[2], DEL.decode("utf8"))
    out = bytes(re.sub("[\]\[]", "", out).replace(", ", DEL.decode("utf8")), "utf8") + EOM
    conn.send(out)


if __name__ == "__main__":

    net, ln = detection.init_net()
    classes = open('../assets/coco.names').read().strip().split('\n')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        init_socket(host, port, s)

        while True:
            conn, addr = s.accept()
            print(f"connected to {addr}")

            with conn:
                img = recv_img(conn)
                img = img_processing(img)

                net_outputs = detection.get_output(img, net, ln)
                pred = detection.tidy_output(net_outputs, img, MIN_CONF)

                print(pred)

                # cv.imshow("Yaaaay", img)
                # cv.waitKey(0)

                send_outputs(pred, conn, classes)
                print("closing connection")
