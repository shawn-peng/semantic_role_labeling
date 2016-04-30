#!/bin/bash

testdir="../data/test/"

for file in `ls $testdir/*conll`;
do
	echo $file
	cut $file -f 3,4,7,5,2,2,2,2,
done
