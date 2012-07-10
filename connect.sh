#!/usr/bin/env bash

host=$1
port=$2

if [[ "$(which rlwrap)" ]]; then
	INPUTRC=inputrc rlwrap nc $host $port

elif [[ "$(which socat)" ]]; then
	INPUTRC=inputrc socat READLINE TCP:$host:$port

else
	nc $host $port

fi
