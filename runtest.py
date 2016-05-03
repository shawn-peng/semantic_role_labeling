#!/bin/python

# import parse
import json
import os
from os import listdir
from os.path import isfile, join
import shutil

from conll12 import *
from parse import *


def evaluate_sentence_srl(block, srls):
    # all roles in dataset
    # number & structure
    true_labels = []

    conll12_get_srl_level_num(block)

    try:
        true_labels = conll12_get_srls(block)
    except ValueError:
        print 'invalid block :', block
        print 'For sentence :', conll12_block2sentence(block)
        print 'in file :', block[0][0]
        exit()

    # print 'true_labels :', true_labels
    n_tlabel = len(true_labels)

    # roles in srl
    # print 'predicted srls', srls
    n_plabel = len(srls)

    # correct in srl
    n_correct = 0
    # false in srl
    n_wrong = 0

    if len(true_labels) == 0:
        print 'No truth SRL'
        # print block
        # raise ValueError
        return 0, n_plabel, n_tlabel

    for srl in srls:
        # check role match
        # match = True
        match = True
        for tsrl in true_labels:
            match = True
            for key in srl:
                # if key in tsrl:
                if tsrl[key] != srl[key]:
                    match = False
                    break

            if match:
                if 'matched' in tsrl and \
                        tsrl['matched'] is not None:

                    print 'duplicate role entry'
                    match = False
                    continue
                    # exit()

                tsrl['matched'] = True
                srl['matched'] = True
                n_correct += 1
                break

        if not match:
            n_wrong += 1

    print 'unrecognized labels :', \
        [l for l in true_labels if 'matched' not in l]

    print 'wrong predictions :', \
        [l for l in srls if 'matched' not in l]

    # print n_correct, n_wrong, n_plabel
    assert n_correct + n_wrong == n_plabel

    return n_correct, n_wrong, n_tlabel


if __name__ == "__main__":
    # get test file list
    testset_dir = 'data/test'
    filelist = [join(testset_dir, f) for f in listdir(
        testset_dir) if isfile(join(testset_dir, f)) and f[0] != '.']

    all_stats = [0] * 3

    num_sent = 0

    # for all test files
    for filename in filelist:
        print filename
        f = open(filename, 'r')
        lines = f.read().split('\n')

        conll = [line.split('\t') for line in lines]

        blocks = split_by_emptyline(conll)

        for block in blocks:
            # print block[0][0]
            if len(block) == 0:
                continue

            print
            print
            num_sent += 1

            sentence = conll12_block2sentence(block)
            # print sentence

            srls = srl_parse(sentence)
            srls = srls[0]

            stats = evaluate_sentence_srl(block, srls)
            print stats
            # print srls
            # exit()

            for i in range(3):
                all_stats[i] += stats[i]

        shutil.move(filename, 'data/test/Store/')

    print all_stats

    print "number of sentences :", num_sent
    print "precision :", 1.0 * all_stats[0] / (all_stats[0] + all_stats[1])
    print "recall :", 1.0 * all_stats[0] / (all_stats[2])
