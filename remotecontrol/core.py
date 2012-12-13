import socket
import threading
import contextlib
import sys
import base64
import pickle


def dumps(x):
    return base64.b64encode(pickle.dumps(x))

def loads(x):
    return pickle.loads(base64.b64decode(x))


_iostack = []
_iostack_lock = threading.Lock()

@contextlib.contextmanager
def replace_stdio(in_=None, out=None, err=None):

    # Replace all stdio with our socket. We are not preventing other threads
    # from executing at the same time so output may end up going in the
    # wrong direction, however we will always restore to the original once
    # all of the clients have finished executing.

    with _iostack_lock:
    
        in_ = in_ or sys.stdin
        out = out or sys.stdout
        err = err or sys.stderr

        _iostack.append((sys.stdin, sys.stderr, sys.stdout))
        sys.stdin = in_
        sys.stdout = out
        sys.stderr = err
     
    try:
        yield
        
    finally:

        # Restore original stdio.
        sys.stdin, sys.stderr, sys.stdout = _iostack.pop()


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


def conform_addr(addr, port=None):

    # Expand collections.
    if isinstance(addr, (list, tuple)):
        if not addr:
            raise ValueError('empty addr list')
        if len(addr) == 1:
            addr = addr[0]
            if port is not None:
                raise TypeError('cannot specify addr as list and a port')
        elif len(addr) == 2:
            addr, port = addr
        else:
            raise ValueError('too many addr elements: %r' % addr)

    type_ = socket.AF_INET

    if isinstance(addr, int) or (isinstance(addr, basestring) and addr.isdigit()):
        addr, port = '', addr

    if port is not None:
        return socket.AF_INET, (addr, int(port))

    else:
        return socket.AF_UNIX, addr



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
        
        self.debug('starting server %s', self.addr)
        
        # Create the server socket.
        self.sock = socket.socket(self.addr_type)
        self.sock.bind(self.addr)
        self.sock.listen(0)
        
        try:
            while True:
                
                sock, addr = self.sock.accept()
                self.debug('new connection %s', addr)
                
                # Spawn a thread with a a client handler.
                client = self.client_class(self, sock, addr, *self.args, **self.kwargs)
                thread = threading.Thread(target=client.interact)
                thread.daemon = True
                thread.start()
        
        except KeyboardInterrupt:
            pass
        
        finally:
            self.debug('shutting down server %r', self.addr)
            self.sock.close()