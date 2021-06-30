# YOLO object detection
import cv2 as cv
import numpy as np

def init_net():
    net = cv.dnn.readNetFromDarknet(
        '../assets/yolov3.cfg', '../assets/yolov3.weights')
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)

    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return net, ln


def get_output(img, net, ln):
    blob = cv.dnn.blobFromImage(
        img, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(ln)
    return outputs


def tidy_output(outputs, img, min_confidence):
    boxes = []
    confidences = []
    classIDs = []
    h, w = img.shape[:2]

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > min_confidence:
                box = detection[:4] * np.array([w, h, w, h])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                box = [x, y, int(width), int(height)]
                boxes.append(box)
                confidences.append(float(confidence))
                classIDs.append(classID)
    return list(zip(boxes, classIDs, confidences))

if __name__ == "__main__":
    img = cv.imread('horse.jpg')
    classes = open('../assets/coco.names').read().strip().split('\n')
    net, ln = init_net()
    outputs = get_output(img, net, ln)
    print(len(tidy_output(outputs, 0.9)))
