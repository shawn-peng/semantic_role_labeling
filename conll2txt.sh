#!/bin/bash

if [ -z "$1" ];
then
	echo "Usage: $0 <CoNLL-X format file>"
	exit 1
fi

if [ ! -e "$1" ];
then
	echo "File \"$1\" does not exist."
	exit 1
fi

if [ ! -f "$1" ];
then
	echo "\"$1\" is not a file."
	exit 1
fi

cat "$1" | cut -f2 |tr '\n' ' '


