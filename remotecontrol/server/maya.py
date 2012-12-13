"""


import autoreload
import remotecontrol.server.maya as rc
autoreload.autoreload(rc)

thread = rc.spawn(('', 9100))



"""

from __future__ import absolute_import

import functools
import code

import maya.utils

from . import generic


class CommandPort(generic.CommandPort):

    def do_eval(self, expr):
        return maya.utils.executeInMainThreadWithResult(eval, expr, self.globals, self.locals)


class Server(generic.Server):

    client_class = CommandPort


listen = functools.partial(generic.listen, server_class=Server)
spawn = functools.partial(generic.spawn, server_class=Server)


if __name__ == '__main__':

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    listen(('', port))

