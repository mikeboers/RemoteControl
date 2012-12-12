import socket
import sys
import threading
import re
import code
import traceback

from .. import core


class CommandPort(object):
    
    def __init__(self, server, sock, addr, locals):
        self.server = server
        self.sock = sock
        self.addr = addr
        self.file = core.fileobject(sock)
        self.locals = {} if locals is None else locals

    def interact(self):
        try:
            while True:
                try:
                    expr = self.file.readline()
                    if not expr:
                        break
                    res = eval(expr, self.locals)
                except KeyboardInterrupt:
                    pass
                except:
                    self.sock.sendall('err: %s\n' % traceback.format_exc().encode('string-escape'))
                else:
                    self.sock.sendall('ok: %s\n' % res)

        finally:
            self.server.debug('shutting down client: %r', self.addr)
            self.sock.close()
            self.file.close


class Server(core.Server):
    
    client_class = CommandPort


def listen(addr, locals=None, server_class=Server):
    if locals is None:
        locals = {}
    console = server_class(addr, locals)
    console.listen()


def spawn(*args, **kwargs):
    thread = threading.Thread(target=listen, args=args, kwargs=kwargs)
    thread.start()
    return thread


if __name__ == '__main__':

    addr = sys.argv[1] if len(sys.argv) > 1 else '9000'
    addr = int(addr) if addr.isdigit() else addr
    listen(addr)


