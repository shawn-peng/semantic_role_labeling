#!/usr/bin/python

import json
from pycorenlp import StanfordCoreNLP
import sys


nlp = StanfordCoreNLP('http://localhost:9000')


def analyze_dep_output(output):
    # print(output['sentences'][0].keys())
    # print(output['sentences'][0]['basic-dependencies'])

    # print output

    sentences = output['sentences']
    print len(sentences)

    srls = []
    # for sents
    for sent in sentences:
    	#print json.dumps(sent.keys())
    	srls.append(analyze_sentence(sent))

    return srls


def analyze_sentence(s):
	deps = s['basic-dependencies']
	#print json.dumps(deps)
	#print ""
	print deps[0]
	vi = deps[0]['dependent']
	# labels = ['*'] * 10
	labels = []
	labels.append(['V',vi,vi+1])
	return labels


'''
@return
	list of role frame list, each frame is a list of semantic roles,
	[VERB, ARG0, ARG1, ...], and each role should specify starting word,
	and ending word
'''
def srl_parse(sentence):
	output = nlp.annotate(sentence, properties={
	    'annotators': 'tokenize,ssplit,pos,depparse,parse',
	    #'outputFormat': 'conllu'
	    'outputFormat': 'json'
	    })

	#Stub, get first verb
	deps = analyze_dep_output(output)

	print deps
	return deps



if __name__ == "__main__":
	if len(sys.argv) < 2:
	    print 'Usage: ' + sys.argv[0] + ' <FILE>'
	    quit(1)

	f = open(sys.argv[1], 'r')
	text = f.read()


	srl = srl_parse(text)


