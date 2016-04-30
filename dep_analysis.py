import json

def analyze_dep_output(output):
    # print(output['sentences'][0].keys())
    # print(output['sentences'][0]['basic-dependencies'])

    # print output

    sentences = output['sentences']
    print len(sentences)

    # for sents
    for sent in sentences:
    	#print json.dumps(sent.keys())
    	analyze_sentence(sent)


def analyze_sentence(s):
	deps = s['basic-dependencies']
	#print json.dumps(deps)
	#print ""
	print deps[0]

