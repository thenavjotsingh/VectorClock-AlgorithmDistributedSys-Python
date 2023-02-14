
from multiprocessing import Process, Pipe
import os
import socket
from threading import Thread
import time
from datetime import datetime

IP = "127.0.0.1"
PORTS = [5566, 5567,5568]
SIZE = 1024
FORMAT = "utf-8"

def get_receiving_vector_clock(recv_time_stamp, vector_clock):
    for id  in range(len(vector_clock)):
        vector_clock[id] = max(recv_time_stamp[id], vector_clock[id])
    return vector_clock

def event(pid, vector_clock):
    vector_clock[pid] += 1
    return vector_clock

def send_msg(pipe, pid, vector_clock):
    vector_clock[pid] += 1
    pipe.send(('', vector_clock))
    return vector_clock

def receive_msg(pipe, pid, vector_clock):
    message, timestamp = pipe.recv()
    vector_clock = get_receiving_vector_clock(timestamp, vector_clock)
    return vector_clock

def createServer(pid, port, pipe1, pipe2):
    print(f"[STARTING]Starting server.....")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    ADDR = (IP, port)
    server.bind(ADDR)
    server.listen(0)
    print(f"[LISTENING] server is listening on {IP}:{port}.....")
    while True:
        conn, addr = server.accept()

def createClient(pid, port, pipe1, pipe2):
    vector_clock = [0,0,0]

    print(f"[PROCESS-{pid}] [CONNECTED] connection established on {IP}:{port}")
    if port == PORTS[0]:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDR = (IP, PORTS[1])
        client.connect(ADDR)
        print(f"[PROCESS-{pid}] before occurance of an event  : " , vector_clock)
        vector_clock = event(pid, vector_clock)
        print(f"[PROCESS-{pid}] after occurance of an event  : " , vector_clock)
        print(f"[PROCESS-{pid}] before sending a message  : " , vector_clock)
        send_msg(pipe1, pid, vector_clock)
        print(f"[PROCESS-{pid}] after sending a message  : " , vector_clock)
    if port == PORTS[1]:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDR = (IP, PORTS[2])
        client.connect(ADDR)
        print(f"[PROCESS-{pid}] before occurance of an event  : " , vector_clock)
        vector_clock = event(pid, vector_clock)
        print(f"[PROCESS-{pid}] after occurance of an event  : " , vector_clock)

        print(f"[PROCESS-{pid}] before receiving a message  : " , vector_clock)
        receive_msg(pipe2, pid, vector_clock)
        print(f"[PROCESS-{pid}] after receiving a message  : " , vector_clock)
    if port == PORTS[2]:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDR = (IP, PORTS[0])
        client.connect(ADDR)
        print(f"[PROCESS-{pid}] before occurance of an event  : " , vector_clock)
        vector_clock = event(pid, vector_clock)
        print(f"[PROCESS-{pid}] after occurance of an event  : " , vector_clock)

        print(f"[PROCESS-{pid}] before sending a message  : " , vector_clock)
        vector_clock = send_msg(pipe1, pid, vector_clock)
        print(f"[PROCESS-{pid}] after sending a message  : " , vector_clock)

        print(f"[PROCESS-{pid}] before receiving a message  : " , vector_clock)
        vector_clock = receive_msg(pipe1, pid, vector_clock)
        print(f"[PROCESS-{pid}] after sending a message  : " , vector_clock)

def createProcess(pid, port, pipe1, pipe2=None):
    server_thread = Thread(target= createServer, args=(pid, port, pipe1, pipe2))
    server_thread.start()
    time.sleep(3)
    client_thread = Thread(target= createClient, args=(pid, port, pipe1, pipe2))
    client_thread.start()
    
if __name__ == '__main__':

    oneandtwo, twoandone = Pipe()
    twoandthree, threeandtwo = Pipe()

    p1= Process(target=createProcess, args=(0, PORTS[0], oneandtwo, ))
    p2= Process(target=createProcess, args=(1, PORTS[1], twoandone, twoandthree ))
    p3= Process(target=createProcess, args=(2, PORTS[2],twoandone ))
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()
