# holoyolo

Client and Server for connection between hololens and pc

## Protocol

### General

- Transmissions end with "\x04" (EOT) character
- Regular delimiter between values is ",\t"

### Specific

- client: "GET _FILESIZE_ _FILE_"
- server: reads _FILESIZE_ bytes and runs yolo
- server: "OK _x_ _y_ _width_ _height_ _classID/name_ _confidence_" (maybe in the future some ERROR code)

## Server

- Download _yolov3.weights_ and _yolov3.cfg_ into assets folder
- $ pip install -r requirements.txt
- $ cd server
- $ python server.py
