import readline
import threading
import socket
import sys

if len(sys.argv) != 3:
    print 'usage: %s host port' % (sys.argv[0])

host, port = sys.argv[1:3]
port = int(port)

sock = socket.create_connection((host, port))

def echo_loop():
    while True:
        x = sock.recv(4096)
        if not x:
            break
        sys.stdout.write(x)
        sys.stdout.flush()

def read_loop():
    while True:
        x = raw_input() + '\n'
        sock.sendall(x)


echo_thread = threading.Thread(target=echo_loop)
echo_thread.start()

read_loop()

