
'''Test file format(CoNLL12)
@http://conll.cemantix.org/2012/data.html

Column	Type	Description
1	Document ID	This is a variation on the document filename
2	Part number	Some files are divided into multiple parts numbered as
	000, 001, 002, ... etc.
3	Word number	
4	Word itself	This is the token as segmented/tokenized in the Treebank.
	Initially the *_skel file contain the placeholder [WORD] which gets replaced by
	the actual token from the Treebank which is part of the OntoNotes release.
5	Part-of-Speech	
6   Parse bit   This is the bracketed structure broken before the first open
	parenthesis in the parse, and the word/part-of-speech leaf replaced with a *.
	The full parse can be created by substituting the asterix with the "([pos]
	[word])" string (or leaf) and concatenating the items in the rows of that
	column.
7   Predicate lemma The predicate lemma is mentioned for the rows for which we
	have semantic role information. All other rows are marked with a "-"
8   Predicate Frameset ID   This is the PropBank frameset ID of the predicate
	in Column 7.
9	Word sense	This is the word sense of the word in Column 3.
10  Speaker/Author  This is the speaker or author name where available. Mostly
	in Broadcast Conversation and Web Log data.
11  Named Entities  These columns identifies the spans representing various
	named entities.
12:N    Predicate Arguments There is one column each of predicate argument
	structure information for the predicate mentioned in Column 7.
N	Coreference	Coreference chain information encoded in a parenthesis structure.
'''


def split_by_emptyline(lines):
    blocks = [[]]
    i = 0
    for line in lines:
        if line[0] == '':
            i += 1
            blocks.append([])
            continue
        blocks[i].append(line)
    return blocks


def conll12_block2sentence(block):
	return ' '.join([w[3] for w in block])