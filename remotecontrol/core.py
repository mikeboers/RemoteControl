import socket
import threading


class fileobject(socket._fileobject):
    """A wrapper around our socket that makes it behave more line a TTY."""
    
    softspace = 0
    
    def isatty(self):
        return True
    
    def flush(self):
        pass
    
    def readline(self, *args):
        return socket._fileobject.readline(self, *args).replace('\r\n', '\n')
    
    def write(self, data):
        self._sock.sendall(data)


def conform_addr(addr):
    type_ = socket.AF_INET
    if isinstance(addr, int):
        addr = ('', addr)
    elif isinstance(addr, basestring):
        type_ = socket.AF_UNIX
    return type_, addr


class Server(object):
    
    client_class = None

    def __init__(self, addr, *args, **kwargs):

        self.addr_type, self.addr = conform_addr(addr)
        self.locals = locals
        self.exec_lock = threading.Lock()

        self.args = args
        self.kwargs = kwargs
    
    def debug(self, msg, *args):
        if args:
            msg = msg % args
        print '# rc: %s' % msg

    def listen(self):
        
        self.debug('starting server %r', self.addr)
        
        # Create the server socket.
        self.sock = socket.socket(self.addr_type)
        self.sock.bind(self.addr)
        self.sock.listen(0)
        
        try:
            while True:
                
                sock, addr = self.sock.accept()
                self.debug('new connection: %r', addr)
                
                # Spawn a thread with a a client handler.
                client = self.client_class(self, sock, addr, *self.args, **self.kwargs)
                threading.Thread(target=client.interact).start()
        
        except KeyboardInterrupt:
            pass
        
        finally:
            self.debug('closing: %r', addr)
            self.sock.close()