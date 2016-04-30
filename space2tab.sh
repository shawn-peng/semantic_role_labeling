#!/bin/bash

testdir="../data/test/"

for file in `ls $testdir/*conll`;
do
	echo $file
	sed -e "s/ \+/\t/g" $file -i
done
