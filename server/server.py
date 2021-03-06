import socket
import cv2 as cv
import numpy as np
import detection
import re
import logging

host, port = '0.0.0.0', 9003
MIN_CONF = 0.2
DEL = b",\t"
EOM = b"\x04"

logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt='%H:%M:%S', level=logging.INFO)


def recv_all(size, conn, part):
    buf = part
    while len(buf) < size:
        packet = conn.recv(size - len(buf))
        buf += packet
        logging.info(f"received {len(packet)} bytes")
        if not packet:
            return None
    return buf


def img_processing(img_bin):
    img_bin = np.array([el for el in img_bin], dtype="uint8")
    return cv.imdecode(img_bin, cv.IMREAD_UNCHANGED)


def recv_img(conn):
    # format: GET imgsize img\x04
    msg = conn.recv(1024)
    logging.debug("msg: ", msg[:20])
    if msg[:4] == b"STOP":
        logging.debug("Got STOP command")
        return None
    cmd, img_size, img_part = msg.split(DEL)
    img_size = int(img_size)
    logging.debug(f"receiving {img_size} bytes")
    img = recv_all(img_size, conn, img_part)
    logging.debug("data:", img[0:20], "...")
    return img


def init_socket(host, port, s):
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    logging.info("server initialized")
    logging.info(f"listening on port {port}")


def send_outputs(pred, conn, classes):
    out = ""
    for output in pred:
        out += "{0}{3}{1}{3}{2}\n".format(
            output[0], classes[output[1]], output[2], DEL.decode("utf8"))
    out = bytes(re.sub("[\]\[]", "", out).replace(
        ", ", DEL.decode("utf8")), "utf8") + EOM
    conn.send(out)


def handle_conn(conn, net, ln, classes):
    with conn:
        while True:
            logging.info("Waiting for image")
            img = recv_img(conn)
            if img == None:
                break

            logging.debug("Decoding image")
            img = img_processing(img)

            logging.info("Processing Image in yolo")
            net_outputs = detection.get_output(img, net, ln)
            pred = detection.tidy_output(net_outputs, img, MIN_CONF)

            # cv.imshow("Yaaaay", img)
            # cv.waitKey(0)

            logging.info("Sending Outputs")
            send_outputs(pred, conn, classes)

        logging.info("closing connection")


if __name__ == "__main__":

    net, ln = detection.init_net()
    classes = open('../assets/coco.names').read().strip().split('\n')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        init_socket(host, port, s)

        while True:
            conn, addr = s.accept()
            print(f"connected to {addr}")

            handle_conn(conn, net, ln, classes)
