import socket
import sys
import threading
import re
import code
import traceback
import pickle
import base64

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
                    expr = expr[:-1]

                    m = re.match(r'^(\w+): ?', expr)
                    if m:
                        command = m.group(1)
                        expr = expr[m.end(0):]
                    else:
                        command = 'eval'

                    expr = expr.decode('string-escape')

                    handler = getattr(self, 'do_' + command)
                    res = handler(expr)

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

    def do_eval(self, expr):
        return eval(expr, self.globals, self.locals)

    def do_set_pickle(self, expr):
        name, value = pickle.loads(base64.b64decode(expr))
        self.locals[name.strip()] = value

    def do_get_pickle(self, name):
        try:
            try:
                value = self.locals[name]
            except KeyError:
                value = self.globals[name]
        except KeyError:
            return ''
        else:
            return base64.b64encode(pickle.dumps(value))



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


