import socket
import sys
import threading
import re

from . import interpreter


class Server(object):
    
    def __init__(self, addr, locals=None):
        self.addr = addr
        self.locals = locals
        self.exec_lock = threading.Lock()
    
    def debug(self, msg, *args):
        if args:
            msg = msg % args
        print '# rc:', msg

    def listen(self):
        
        self.debug('starting server %r', self.addr)
        
        # Create the server socket.
        self.sock = socket.socket(socket.AF_INET)
        self.sock.bind(self.addr)
        self.sock.listen(0)
        
        try:
            while True:
                
                sock, addr = self.sock.accept()
                self.debug('new connection: %r', addr)
                
                # Spawn a thread with a a client handler.
                client = interpreter.Interpreter(self, self.locals, sock, addr)
                threading.Thread(target=client.interact).start()
        
        except KeyboardInterrupt:
            pass
        
        finally:
            self.debug('closing: %r', addr)
            self.sock.close()


def listen(addr, locals=None):
    if locals is None:
        locals = {}
    if isinstance(addr, int):
        addr = ('', addr)
    console = Server(addr, locals)
    console.listen()


def spawn(*args, **kwargs):
    thread = threading.Thread(target=listen, args=args, kwargs=kwargs)
    thread.start()
    return threan


if __name__ == '__main__':

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    listen(('', port))


