import sys
import threading
import re
import traceback

from . import threads
from . import core


class FakeIO(object):

    def __init__(self, port, type, forward=None):
        self.port = port
        self.type = type
        self.forward = forward

    def write(self, msg):
        self.port.sock.sendall('%s: %s\n' % (self.type, str(msg).encode('string-escape')))
        if self.forward:
            self.forward.write(msg)

    def flush(self):
        if self.forward:
            self.forward.flush()


class CommandPort(object):
    
    def __init__(self, server, sock, addr, globals=None, locals=None):
        self.server = server
        self.sock = sock
        self.addr = addr
        self.file = core.fileobject(sock)

        self._stdout = FakeIO(self, 'stdout', sys.stdout)
        self._stderr = FakeIO(self, 'stderr', sys.stderr)

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
                    
                    with core.replace_stdio(None, self._stdout, self._stderr):
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

    def do_exec(self, expr):
        return eval(compile(expr, '<remote>', 'exec'), self.globals, self.locals)
    
    def do_call(self, expr):
        
        parts = expr.strip().split()
        parts = [core.loads(x) for x in parts]
        while len(parts) < 4:
            parts.append(None)

        func, args, kwargs, opts = parts

        func = _get_func(func)
        args = args or ()
        kwargs = kwargs or {}
        opts = opts or {}

        try:
            res = {
                'status': 'ok',
                'res': self._do_call(func, args, kwargs, opts),
            }

        # This does not capture SystemExit or KeyboardInterrupt, which we do
        # not want to pass through the barrier.
        except Exception as e:
            res = {
                'status': 'exception',
                'type': e.__class__,
                'args': e.args,
            }
        return core.dumps(res)

    def _do_call(self, func, args, kwargs, opts):
        if opts.get('main_thread', True):
            return threads.call_in_main_thread(func, *args, **kwargs)
        else:
            return func(*args, **kwargs)

    def do_set_pickle(self, expr):
        name, value = core.loads(expr)
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
            return core.dumps(value)


def _get_func(spec):
    if not isinstance(spec, basestring):
        return spec
    m = re.match(r'([\w\.]+):([\w]+)$', spec)
    if not m:
        raise ValueError('string funcs must be for form "package.module:function"')
    mod_name, func_name = m.groups()
    mod = __import__(mod_name, fromlist=['.'])
    return getattr(mod, func_name)


class Server(core.Server):
    
    client_class = CommandPort


def listen(addr, globals=None, locals=None, server_class=Server):
    console = server_class(addr, globals, locals)
    console.listen()


def spawn(*args, **kwargs):
    thread = threading.Thread(target=listen, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread


if __name__ == '__main__':

    addr = sys.argv[1] if len(sys.argv) > 1 else '9000'
    addr = int(addr) if addr.isdigit() else addr
    listen(addr, {})


