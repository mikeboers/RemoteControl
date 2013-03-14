"""

gdb --interpreter=mi -nx <<EOF
set auto-solib-add off
set unwindonsignal on
set unwind-on-terminating-exception on
attach $1
sharedlibrary libc
sharedlibrary libdl
call dlopen("/home/mboers/key_tools/remotecontrol/libinject.dylib", RTLD_NOW)
print ((char*)(dlerror()))
sharedlibrary /home/mboers/key_tools/remotecontrol/libinject.dylib
call remotecontrol_py_init
detach
quit

"""

import subprocess
import sys
import os


pid = int(sys.argv[1])
lib = os.path.abspath(os.path.join(os.path.dirname(__file__), 'libinject.so'))
entrypoint = 'remotecontrol_py_init'

gdb = subprocess.Popen(['gdb', '--interpreter=mi', '-nx'], stdin=subprocess.PIPE)

gdb.stdin.write('''set auto-solib-add off
set unwindonsignal on
set unwind-on-terminating-exception on
attach %(pid)d
sharedlibrary libc
call printf("hello\\n")
sharedlibrary libdl
call dlopen("%(lib)s", RTLD_NOW)
print ((char*)(dlerror()))
sharedlibrary %(lib)s
call %(entrypoint)s()
detach
quit
''' % globals())

gdb.wait()
