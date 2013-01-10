import functools
import glob
import Queue as queue
import re
import select
import socket
import sys
import threading


from . import core


_shutdown_lock = threading.Lock()



class CmdsProxy(object):

    def __init__(self, proc):
        self._proc = proc

    def __getattr__(self, name):
        return functools.partial(self._proc, 'maya.cmds:%s' % name)


class CommandSock(object):

    def __init__(self, addr):
        
        self.addr_type, self.addr = core.conform_addr(addr)
        self.sock = socket.socket(self.addr_type)
        self.sock.connect(self.addr)

        self.buffer = ''
        self.lock = threading.Lock()

    def send(self, msg):
        self.sock.sendall(msg)

    def recv(self, timeout=None):
        with self.lock:

            while '\n' not in self.buffer:

                # Wait for it to be ready.
                rlist, _, _ = select.select([self.sock], [], [], timeout)
                if not rlist:
                    raise RuntimeError('timeout')

                # Read!
                new = self.sock.recv(8096)
                self.buffer += new
                
                # EOF.
                if not new:
                    break

            # If we don't have a complete message, it is likely due to
            # an EOF, so just return None.
            try:
                msg, self.buffer = self.buffer.split('\n', 1)
            except ValueError:
                return None
            else:
                return msg

    def __getattr__(self, name):
        return getattr(self.sock, name)


class CommandPort(object):

    def __init__(self, addr=None, unix_glob=None):
        
        if addr:
            self._sock = CommandSock(addr)

        elif unix_glob:
            for addr in glob.glob(unix_glob):
                try:
                    self._sock = CommandSock(addr)
                except socket.error:
                    continue
                else:
                    break
            else:
                raise ValueError('could not glob a socket')

        else:
            raise ValueError('must specify addr or unix_glob')

        self._res_queue = queue.Queue()

        # Start the event loop.
        self._thread = threading.Thread(target=self._event_loop)
        self._thread.daemon = True
        self._thread.start()

        # Setup command proxy.
        self.cmds = CmdsProxy(self)

    def __del__(self):
        self.close()

    def close(self):
        self._sock.close()

    def _event_loop(self):
        
        while True:
            msg = self._sock.recv()
            if msg is None:
                # Put something on the result queue so that things don't
                # block forever. Ideally we would make the queue non-blocking.
                self._res_queue.put((False, RuntimeError('socket closed')))
                break

            m = re.match(r'^(\w+): ?', msg)
            if not m:
                raise RuntimeError('bad message from server: %r' % msg)

            command = m.group(1)
            msg = msg[m.end(0):].decode('string-escape')
            handler = getattr(self, '_on_%s' % command)
            handler(msg)

    def _on_ok(self, msg):
        self._res_queue.put((True, msg))

    def _on_exc(self, msg):
        self._res_queue.put((False, msg))

    def _on_stdout(self, msg):
        sys.stdout.write(msg)
        sys.stdout.flush()

    def _on_stderr(self, msg):
        sys.stderr.write(msg)
        sys.stderr.flush()

    def raw_call(self, command, expr):

        if command:
            expr = '%s: %s' % (command, expr)
        self._sock.send(expr.rstrip().encode('string-escape') + '\n')

        ok, res = self._res_queue.get()
        if ok:
            return res
        else:
            raise RuntimeError('error from remote: %s' % res)

    def call(self, func, args=None, kwargs=None, **opts):
        
        res = self.raw_call('call', '%s %s %s %s' % tuple(core.dumps(x) for x in (func, args, kwargs, opts)))
        res = core.loads(res)

        if res.get('status') == 'ok':
            return res['res']

        if res.get('status') == 'exception':
            raise res['type'](*res['args'])

        raise RuntimeError('bad call response: %r' % res)

    def __call__(self, func, *args, **kwargs):
        return self.call(func, args, kwargs)

    def eval(self, *args, **kwargs):
        return self.call(eval, args, **kwargs)

    def exec_(self, source, **kwargs):
        self.raw_call('exec', source)

    def mel(self, expr, **kwargs):
        return self.call('maya.mel:eval', [expr], **kwargs)

    def __setitem__(self, name, value):
        self.raw_call('set_pickle', core.dumps((name, value)))

    def __getitem__(self, name):
        res = self.raw_call('get_pickle', name)
        if not res:
            raise KeyError(name)
        return core.loads(res)


# Convenient!
open = CommandPort




if __name__ == '__main__':
    __name__ = 'remotecontrol.client'
    port = CommandPort(sys.argv[1:])

