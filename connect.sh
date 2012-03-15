host=$1
port=$2

INPUTRC=inputrc socat READLINE TCP:$host:$port