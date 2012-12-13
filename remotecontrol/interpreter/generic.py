import socket
import sys
import threading
import re
import code

from .. import core


class Interpreter(code.InteractiveConsole):
    
    iostack = []
    
    def __init__(self, server, sock, addr, locals):
        self.server = server
        self.sock = sock
        self.addr = addr
        self.file = core.fileobject(sock)
        code.InteractiveConsole.__init__(self, locals={} if locals is None else locals)
        
    def raw_input(self, prompt):
        
        self.sock.sendall(prompt)
        
        # We will get an empty string when the connection has closed. We must 
        # manually throw an EOFError (which the super will handle), otherwise
        # the socket will complain of a bad pipe when it tries to write the
        # next prompt.
        x = self.file.readline()
        if not x:
            raise EOFError()
        return x
    
    def write(self, content):
        self.sock.sendall(content)
    
    def push(self, line):
        
        # Replace all stdio with our socket. We are not preventing other threads
        # from executing at the same time so output may end up going in the
        # wrong direction, however we will always restore to the original once
        # all of the clients have finished executing.
        self.iostack.append((sys.stdin, sys.stderr, sys.stdout))
        sys.stdin = sys.stderr = sys.stdout = self.file
            
        try:
            return code.InteractiveConsole.push(self, line)
            
        finally:
            # Restore original stdio.
            sys.stdin, sys.stderr, sys.stdout = self.iostack.pop()
    
    def runsource(self, source, *args):
        
        # Fix a shortcoming of the super class: it does not handle multiple
        # lines in control flow the same way that the "real" interpreter does.
        # Assert that if we are in some control flow then the last line must be
        # empty before we attempt to exec it.
        lines = source.splitlines()
        if len(lines) > 1 and lines[-1].strip():
            return True
        
        return self._runsource(source, *args)

    def _runsource(self, source, *args):
        return code.InteractiveInterpreter.runsource(self, source, *args)
    
    def interact(self):
        try:
            code.InteractiveConsole.interact(self)
        finally:
            self.server.debug('shutting down client %s', self.addr)
            self.sock.close()
            self.file.close


class Server(core.Server):

    client_class = Interpreter



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


