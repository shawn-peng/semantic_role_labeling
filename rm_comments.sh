#!/bin/bash

testdir="../data/test/"

for file in `ls $testdir/*conll`;
do
	echo $file
	sed -e "/^#.*/d" $file -i
done
