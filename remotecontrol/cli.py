#!/usr/bin/env python

import optparse
import glob
import socket
import subprocess
import os

import remotecontrol.core


parser = optparse.OptionParser()

parser.add_option('--app')
parser.add_option('-m', '--maya', action='store_const', dest='app', const='maya')
parser.add_option('-n', '--nuke', action='store_const', dest='app', const='nuke')
parser.add_option('--rv',         action='store_const', dest='app', const='rv')
parser.add_option('--houdini',    action='store_const', dest='app', const='houdini')
parser.add_option('--mari',       action='store_const', dest='app', const='mari')

parser.add_option('-r', '--raw', dest='raw', action='store_true')
parser.add_option('-i', '--interactive', dest='python', action='store_true')

def main():

    opts, args = parser.parse_args()

    addr = None
    unix_glob = None

    if opts.app:
        if opts.raw or opts.python:
            unix_glob = '/var/tmp/remotecontrol.%s.*.cmdsock' % opts.app
        else:
            unix_glob = '/var/tmp/remotecontrol.%s.*.pysock' % opts.app


    if not unix_glob and not args:
        parser.print_usage()
        exit(1)

    if args:
        _, addr = remotecontrol.core.conform_addr(*args)

    else:
        sock = socket.socket(socket.AF_UNIX)
        for addr in glob.glob(unix_glob):
            print addr
            try:
                sock.connect(addr)
                break
            except Exception as e:
                print e
                continue
        else:
            print 'could not find socket'
            exit(2)
        sock.close()



    def which(cmd):
        proc = subprocess.Popen(['which', cmd], stdout=subprocess.PIPE)
        out, err = proc.communicate()
        return out.strip()


    environ = dict(os.environ)

    if opts.python:
        cmd = ['python', '-im', 'remotecontrol.client', addr]

    else:

        if isinstance(addr, basestring):
            cmd = ['nc', '-U', addr]
        else:
            cmd = ['nc', addr[0], str(addr[1])]

        if which('rlwrap'):
            environ['INPUTRC'] = os.path.abspath(os.path.join(__file__, '..', '..', 'inputrc'))
            cmd.insert(0, 'rlwrap')

    os.execvpe(cmd[0], cmd, environ)


