#!/bin/python

#import parse
import json
import os
from os import listdir
from os.path import isfile, join

from conll12 import *
from parse import *


if __name__ == "__main__":
    # get test file list
    testset_dir = 'data/test'
    filelist = [join(testset_dir, f) for f in listdir(testset_dir) if isfile(join(testset_dir, f))]

    # for all test files
    for filename in filelist:
        f = open(filename, 'r')
        lines = f.read().split('\n')
        conll = []
        for line in lines:
            conll.append(line.split('\t'))

        blocks = split_by_emptyline(conll)

    for block in blocks:
    	sentence = conll12_block2sentence(block)

    	srl = srl_parse(sentence)
    	quit()
