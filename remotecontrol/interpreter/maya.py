"""


import autoreload
import remotecontrol.interpreter.maya as rc
autoreload.autoreload(rc)

thread = rc.spawn(('', 9100))



"""

from __future__ import absolute_import

import functools
import code

import maya.utils

from . import generic


class Interpreter(generic.Interpreter):

    def _call_in_main_thread(self, func, *args):
        return maya.utils.executeInMainThreadWithResult(func, *args)


class Server(generic.Server):

    client_class = Interpreter


listen = functools.partial(generic.listen, server_class=Server)
spawn = functools.partial(generic.spawn, server_class=Server)


if __name__ == '__main__':

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    listen(('', port))

