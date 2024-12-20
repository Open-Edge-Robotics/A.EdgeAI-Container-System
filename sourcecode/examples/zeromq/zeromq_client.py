
import zmq
import time

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5555")

request = 0
while True:
    request += 1
    print("Sending request %s …" % request)
    s = f"Hello {request}" 
    socket.send(s.encode('utf-8'))

    time.sleep(1)
