
'''Test file format(CoNLL12)
@http://conll.cemantix.org/2012/data.html

Column  Type    Description
1   Document ID This is a variation on the document filename
2   Part number Some files are divided into multiple parts numbered as
    000, 001, 002, ... etc.
3   Word number
4   Word itself This is the token as segmented/tokenized in the Treebank.
    Initially the *_skel file contain the placeholder [WORD] which gets
    replaced by the actual token from the Treebank which is part of the
    OntoNotes release.
5   Part-of-Speech
6   Parse bit   This is the bracketed structure broken before the first open
    parenthesis in the parse, and the word/part-of-speech leaf replaced with
    a *. The full parse can be created by substituting the asterix with
    the "([pos] [word])" string (or leaf) and concatenating the items in the
    rows of that column.
7   Predicate lemma The predicate lemma is mentioned for the rows for which we
    have semantic role information. All other rows are marked with a "-"
8   Predicate Frameset ID   This is the PropBank frameset ID of the predicate
    in Column 7.
9   Word sense  This is the word sense of the word in Column 3.
10  Speaker/Author  This is the speaker or author name where available. Mostly
    in Broadcast Conversation and Web Log data.
11  Named Entities  These columns identifies the spans representing various
    named entities. 12:N Predicate Arguments There is one column each of
    predicate argument structure information for the predicate mentioned in
    Column
7. N   Coreference Coreference chain information encoded in a parenthesis
    structure.
'''

import re
import string


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
    # print block
    # if len(block) > 1:
    return ' '.join([w[3] for w in block])
    # s = ''
    # hyph_prev = False
    # for entry in block:
    #     word = entry[3]
    #     if word != '-':
    #         if not hyph_prev:
    #             s += ' ' + word
    #         else:
    #             s += word
    #         hyph_prev = False
    #     else:
    #         s += word
    #         hyph_prev = True
    # return s
    # else:
    #     return block[0][3]


def conll12_content2sentences(content):
    return ' '.join([w[3] for w in content])


def conll12_get_srl_level_num(block):
    return len(block[0]) - 12


def conll12_parse_role(state, embeded_lvl, rolestr):
    if state == 'empty':
        if rolestr[0] == '(':
            try:
                role = re.search(
                    '^\(([A-Z0-9-]+)(\([A-Z0-9-]+)*\*\)*$', rolestr).group(1)
            except AttributeError:
                print 'Error parse role string :' + rolestr
                role = None
                raise ValueError

            a = rolestr.count('(')
            b = rolestr.count(')')
            if a == b:
                state = 'empty'
            elif a > b:
                state = 'started'
                embeded_lvl = a - b
            else:
                print 'Error parse role string :' + rolestr
                role = None
                raise ValueError

        elif rolestr == '*':
            role = None
        else:
            print 'Error state role pair in parse role : \
                <' + state + ', ' + rolestr + '>'
            raise ValueError

    elif state == 'started':
        if rolestr == '*':
            role = None
        elif rolestr == '*)':
            embeded_lvl -= 1
            if embeded_lvl == 0:
                state = 'empty'
                role = None
            elif embeded_lvl > 0:
                role = None
            else:
                print 'Embeded role level pop downflow'
                raise ValueError
        elif rolestr == '*))':
            embeded_lvl -= 2
            if embeded_lvl == 0:
                state = 'empty'
                role = None
            elif embeded_lvl > 0:
                role = None
            else:
                print 'Embeded role level pop downflow'
                raise ValueError
        elif rolestr == '*)))':
            print 'Warning: 3 layer embeded role'
            embeded_lvl -= 3
            if embeded_lvl == 0:
                state = 'empty'
                role = None
            elif embeded_lvl > 0:
                role = None
            else:
                print 'Embeded role level pop downflow'
                raise ValueError
        else:
            print 'Embeded role :', rolestr
            # ignore embeded
            # state = 'started'
            a = rolestr.count('(')
            b = rolestr.count(')')
            embeded_lvl += a - b
            role = None
            # print 'Error state role pair in parse role : \
            #     <' + state + ', ' + rolestr + '>'
            # raise ValueError

    else:
        print 'Error state role pair in parse role : \
            <' + state + ', ' + rolestr + '>'
        raise ValueError

    return state, embeded_lvl, role


def conll12_get_srls(block):
    '''
    @return
        list of role frame list, each frame is a list of semantic roles,
        [VERB, ARG0, ARG1, ...], and each role should specify starting word,
        and ending word
    '''
    nlayer = conll12_get_srl_level_num(block)
    nlen = len(block)

    # expected_roles = ['V', 'ARG0', 'ARG1', 'ARG2']
    expected_roles = ['V', 'ARG0', 'ARG1']
    srls = []
    cur_role = None
    state = 'empty'
    embeded_lvl = 0
    for i in range(nlayer):
        # find V first
        cur_verb = None
        for j in range(nlen):
            role = block[j][11 + i]
            if role == '(V*)':
                cur_verb = j

        if cur_verb is None:
            print i
            raise ValueError

        for j in range(nlen):
            role = block[j][11 + i]
            if role != '*':
                try:
                    state, embeded_lvl, role = conll12_parse_role(
                        state, embeded_lvl, role)
                except ValueError:
                    print i, j, cur_role
                    print srls
                    exit()

                if state == 'started':
                    if role is not None:
                        cur_role = {'role': role,
                                    'vind': cur_verb, 'start': j}
                    else:
                        # meet some embeded role, skip this
                        pass

                elif state == 'empty':
                    if role is not None:
                        cur_role = {'role': role, 'vind': cur_verb,
                                    'start': j, 'end': j + 1}
                    else:
                        if cur_role is None:
                            print "Error in parse srl from CoNLL"
                            print "last state and role :", state, role
                            print "Cursor pos :", i, j
                            raise ValueError

                        cur_role['end'] = j + 1

                    if cur_role['role'] in expected_roles:
                        srls.append(cur_role)

                    cur_role = None

                else:
                    print "Error in parse srl from CoNLL"
                    print "last state and role :", state, role
                    raise ValueError

                # print state, role
        # check state
        if state != 'empty':
            print 'find not ended role.'
            cur_role['end'] = j + 1
            if cur_role['role'] in expected_roles:
                srls.append(cur_role)
            state = 'empty'

    return srls
