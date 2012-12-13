import socket
import sys
import threading
import re
import code
import traceback

from .. import core


class CommandPort(object):
    
    def __init__(self, server, sock, addr, globals=None, locals=None):
        self.server = server
        self.sock = sock
        self.addr = addr
        self.file = core.fileobject(sock)

        # Take extra care to pass anything that isn't None through.
        self.globals = {} if globals is None else globals
        self.locals = {} if locals is None else locals

    def interact(self):
        try:
            while True:
                try:
                    expr = self.file.readline()
                    if not expr:
                        break
                    res = self.eval(expr, self.globals, self.locals)
                except KeyboardInterrupt:
                    pass
                except:
                    self.sock.sendall('exc: %s\n' % traceback.format_exc().encode('string-escape'))
                else:
                    self.sock.sendall('ok: %s\n' % str(res).encode('string-escape'))

        finally:
            self.server.debug('shutting down client %s', self.addr)
            self.sock.close()
            self.file.close

    def eval(self, expr, globals, locals):
        return eval(expr, globals, locals)



class Server(core.Server):
    
    client_class = CommandPort


def listen(addr, globals=None, locals=None, server_class=Server):
    console = server_class(addr, globals, locals)
    console.listen()


def spawn(*args, **kwargs):
    thread = threading.Thread(target=listen, args=args, kwargs=kwargs)
    thread.start()
    return thread


if __name__ == '__main__':

    addr = sys.argv[1] if len(sys.argv) > 1 else '9000'
    addr = int(addr) if addr.isdigit() else addr
    listen(addr, {})


