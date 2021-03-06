#!/bin/bash

if [ -z "$1" ];
then
	echo "Usage: $0 <FILE>"
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

#java -mx150m -cp "./stanford-corenlp-full-2015-12-09/*:" edu.stanford.nlp.parser.nndep.DependencyParser -outputFormat "conll" -textFile "$1" -outFile -

java -mx2g -cp "stanford-corenlp-full-2015-12-09/*" edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,depparse -file "$1" -outputFormat "CoNLLU" -outputFile -





