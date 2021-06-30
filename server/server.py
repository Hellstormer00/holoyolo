import socket
import cv2 as cv
import numpy as np
import detection

host, port = '172.22.223.57', 9002
MIN_CONF = 0.9

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


def recv_img(conn):
    img_size = int(conn.recv(1024))
    print(f"receiving {img_size} bytes")
    img = recv_all(img_size, conn)
    print("data:", img[0:20], "...")
    return img


def init_socket(host, port, s):
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    print("server initialized")
    print("listening on port", port)


def send_outputs(pred, conn):
    out = ""
    for output in pred:
        out += f"{output[0]},{output[1]},{output[2]}\n"
    conn.send(bytes(output))

if __name__ == "__main__":

    net, ln = detection.init_net()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        init_socket(host, port, s)

        while True:
            conn, addr = s.accept()
            print(f"connected to {addr}")

            with conn:
                # img = recv_img(conn)
                # img = img_processing(img)

                img = cv.imread('horse.jpg')
                
                net_outputs = detection.get_output(img, net, ln)
                pred = detection.tidy_output(net_outputs, img, MIN_CONF)

                print(pred)

                # cv.imshow("Yaaaay", img)
                # cv.waitKey(0)

                send_outputs(pred, conn)
                print("closing connection")
