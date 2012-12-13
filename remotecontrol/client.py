import base64
import pickle
import glob
import socket
import os
import select
import re
import tempfile
import functools
import threading
import sys


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
                rlist, _, _ = select.select([self.sock], [], [], timeout)
                if not rlist:
                    raise RuntimeError('timeout')
                self.buffer += self.sock.recv(8096)
            msg, self.buffer = self.buffer.split('\n', 1)
            return msg

    def __getattr__(self, name):
        return getattr(self.sock, name)


class CommandPort(object):

    def __init__(self, addr=None, unix_glob=None):
        
        if addr:
            self.sock = CommandSock(addr)

        elif unix_glob:
            for addr in glob.glob(unix_glob):
                try:
                    self.sock = CommandSock(addr)
                except socket.error:
                    continue
                else:
                    break
            else:
                raise ValueError('could not glob a socket')

        else:
            raise ValueError('must specify addr or unix_glob')

        # Setup command proxy.
        self.cmds = CmdsProxy(self)

    def __del__(self):
        self.close()

    def close(self):
        self.sock.close()

    def raw_call(self, command, expr):

        if command:
            expr = '%s: %s' % (command, expr)
        self.sock.send(expr.rstrip().encode('string-escape') + '\n')
        res = self.sock.recv()

        # Deal with the raw transport encoding.
        if res.startswith('ok: '):
            res = res[4:].decode('string-escape')
        elif res.startswith('exc: '):
            res = res[5:].decode('string-escape')
            raise RuntimeError('error from remote: %s' % res)
        else:
            raise RuntimeError('bad message: %r' % res)

        return res

    def call(self, func, args=None, kwargs=None, timeout=None):
        package = base64.b64encode(pickle.dumps((func, args or (), kwargs or {})))
        expr = '__import__(%r, fromlist=["."])._dispatch(%r)' % (__name__, package)

        res = self.raw_call(None, expr)

        # Deal with high-level encoding.
        res = pickle.loads(base64.b64decode(res))
        if res.get('status') == 'ok':
            return res['res']
        if res.get('status') == 'exception':
            raise res['type'](*res['args'])
        raise RuntimeError('bad response: %r' % res)

    def __call__(self, func, *args, **kwargs):
        return self.call(func, args, kwargs)

    def eval(self, *args, **kwargs):
        return self.call(eval, args, **kwargs)

    def mel(self, expr, **kwargs):
        return self.call('maya.mel:eval', [expr], **kwargs)

    def __setitem__(self, name, value):
        self.raw_call('set_pickle', base64.b64encode(pickle.dumps((name, value))))

    def __getitem__(self, name):
        res = self.raw_call('get_pickle', name)
        if not res:
            raise KeyError(name)
        return pickle.loads(base64.b64decode(res))


# Convenient!
open = CommandPort


def _get_func(spec):
    if not isinstance(spec, basestring):
        return spec
    m = re.match(r'([\w\.]+):([\w]+)$', spec)
    if not m:
        raise ValueError('string funcs must be for form "package.module:function"')
    mod_name, func_name = m.groups()
    mod = __import__(mod_name, fromlist=['.'])
    return getattr(mod, func_name)


def _dispatch(package):
    func, args, kwargs = pickle.loads(base64.b64decode(package))
    func = _get_func(func)
    try:
        res = dict(status='ok', res=func(*args, **kwargs))
    except Exception as e:
        res = dict(status='exception', type=e.__class__, args=e.args)
    return base64.b64encode(pickle.dumps(res))


if __name__ == '__main__':
    __name__ = 'remotecontrol.client'
    port = CommandPort(sys.argv[1:])

