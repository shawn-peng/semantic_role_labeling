#!/bin/bash

pushd stanford-corenlp-full-2015-12-09

java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer

popd

