#!/usr/bin/python

import json
from pycorenlp import StanfordCoreNLP
import sys
import re


nlp = StanfordCoreNLP('http://localhost:9000')


def analyze_dep_output(output):
    # print(output['sentences'][0].keys())
    # print(output['sentences'][0]['basic-dependencies'])

    # print output

    sentences = output['sentences']
    print 'number of sentences :', len(sentences)

    if len(sentences) > 1:
        # print sentences
        pass

    srls = []
    # for sents
    for sent in sentences:
        # print json.dumps(sent.keys())
        srls.append(analyze_sentence(sent))

    return srls


def find_dep(deps, deptypes, index):
    ndep = filter(lambda d: d['dep'] in deptypes and
                  d['governor'] == index + 1, deps)
    if len(ndep) < 1:
        # print json.dumps(ndep)
        # raise ValueError
        print 'dependent with', deptypes, 'can not be found for:', index
        return None
    elif len(ndep) > 1:
        print 'found more than one dep for:', index
        dep = min(ndep, key=lambda d: d['dependent'] - index - 1)
    else:
        dep = ndep[0]

    return dep


def find_gov(deps, deptypes, index):
    ndep = filter(lambda d: d['dep'] in deptypes and
                  d['dependent'] == index + 1, deps)
    if len(ndep) < 1:
        # print json.dumps(ndep)
        # raise ValueError
        print 'governor with', deptypes, 'can not be found for:', index
        return None
    elif len(ndep) > 1:
        print 'found more than one governor dep for:', index
        dep = min(ndep, key=lambda d: d['dependent'] - index - 1)
    else:
        dep = ndep[0]

    ngov = filter(lambda d: d['dependent'] == dep['governor'], deps)
    # print ngov
    # assert len(ngov) == 1
    if len(ngov) > 1:
        print 'dep', dep, 'has mor than one governor'

    return ngov[0]


def get_descendants(deps, si, reg_allowed, reg_filtered):
    # dset = [entry, get_descendants(deps, entry, entry['dependent'] - 1)
    #         for entry in deps if entry['governor'] == si + 1]
    dset = []
    for entry in deps:
        if entry['governor'] == si + 1 and \
                entry['governor'] != entry['dependent']:
            if re.match(reg_filtered, entry['dep']) is not None:
                # filter
                pass
            elif re.match(reg_allowed, entry['dep']) is not None:
                dset.append(entry)
                dset += get_descendants(deps, entry['dependent'] - 1,
                                        reg_allowed, reg_filtered)
            else:
                continue
                # Exception
                print 'encountered unexpected dep type when '\
                    'get_descendants() :', entry['dep']
                print entry, reg_allowed, reg_filtered
                raise ValueError

    return dset


def get_start_end(descendants, si):
    start = si
    end = si + 1
    for entry in descendants:
        index = entry['dependent'] - 1
        if index < start:
            start = index
        elif index + 1 > end:
            end = index + 1
    return start, end


def find_subject(deps, tokens, vdep, vi):
    subdep = find_dep(deps, ['nsubj', 'nmod:agent'], vi)
    if subdep is not None:
        si = subdep['dependent'] - 1
        if tokens[si]['pos'] == 'WDT':  # which, who, that
            print 'the subject is subcordinate :', subdep
            # find preceding word
            subdep = find_gov(deps, ['acl:relcl'], vi)
            assert subdep is not None

            return subdep, 'acl:relcl'

        return subdep, subdep['dep']
    else:
        if vdep['dep'] in ['xcomp', 'conj:and', 'conj']:
            # find subject of govener
            gdep = find_gov(deps, [vdep['dep']], vi)
            assert gdep is not None
            # find subject of govener
            return find_subject(deps, tokens, gdep, gdep['dependent'] - 1)
        else:
            return None, None

    assert 0
    return None, None


def find_object(deps, vdep, vi):
    objdep = find_dep(deps, ['dobj', 'nsubjpass', 'ccomp'], vi)
    if objdep is not None:
        return objdep
    else:
        if vdep['dep'] in ['xcomp', 'conj:and', 'conj']:
            # find subject of govener
            gdep = find_gov(deps, [vdep['dep']], vi)
            assert gdep is not None
            # find subject of govener
            return find_object(deps, gdep, gdep['dependent'] - 1)
        else:
            return None


def check_has_dep(deps, deptype, index):
    dep = find_dep(deps, [deptype], index)
    return dep is not None


def check_has_deps(deps, deptypes, index):
    for dt in deptypes:
        if not check_has_dep(deps, dt, index):
            return False
    return True


def analyze_sentence(s):
    # deps = s['basic-dependencies']
    deps = s['collapsed-ccprocessed-dependencies']
    # print s.keys()
    tokens = s['tokens']
    # print json.dumps(tokens)
    # print json.dumps(deps)
    # print ''
    # print deps[0]
    althead = False

    # find all verbs
    mdeps = ['ROOT', 'root', 'ccomp', 'xcomp',
             'acl:relcl', 'acl', 'conj:and', 'advcl',
             'parataxis']

    preceding_allowing = '(det|amod|compound|nmod:of|nummod|advmod'\
        '|neg|nmod:to)'
    preceding_filtered = '(punct|acl:relcl|case|nsubj|cop|conj:or'\
        '|dep|cc|conj:and|aux|conj:but|advcl|conj|nmod:as)'
    # preceding_filtered = ''
    verbdeps = [d for d in deps if d['dep'] in mdeps]
    # print verbdeps

    labels = []
    for vdep in verbdeps:
        vi = vdep['dependent'] - 1
        pos, word = tokens[vi]['pos'], tokens[vi]['word']
        # follow_dep = []
        if pos[0] != 'V':
            if pos[0] in ['N', 'J'] or pos in ['DT', 'CD', '$']:
                # if check_has_dep(deps, 'case', vi):
                #     pass
                # else:
                #     continue
                pass
            elif pos in ['``', 'PRP', 'MD', 'RB', 'CC', 'UH', 'IN']:
                continue
            elif pos in ['WP', ':']:
                pass
            else:
                print 'unexpected pos:', pos, 'at position :', vi
                continue
                raise ValueError
            print pos, word
            # find cop
            vdep = find_dep(deps, ['cop'], vi)
            # vdep = filter(lambda d: d['dep'] == 'cop' and
            #               d['governor'] == vi + 1, deps)
            if vdep is None:
                print 'can not find cop verb for complement', \
                    vi, tokens[vi]['word']
                # json.dumps(deps), vi
                # no further role could be labeled
                continue

            # assert len(vdep) == 1
            # print vdep
            if pos[0] in ['N', 'J'] or pos in ['DT', 'CD', '$']:
                althead = True
                headi = vi

            vi = vdep['dependent'] - 1
            pos, word = tokens[vi]['pos'], tokens[vi]['word']
            # vi = vdep['dependent'] - 1
            # pos, word = tokens[vi]['pos'], tokens[vi]['word']
            print pos, word
            assert pos[0] == 'V'

        # exit()

        # labels = ['*'] * 10
        labels.append({'role': 'V', 'start': vi,
                       'end': vi + 1, 'vind': vi})

        # find arg0: with dep [nsubj]
        ds = None

        if althead:
            subdep = find_dep(
                deps, ['nsubj', 'nmod:agent', 'csubj'], headi)
        else:
            subdep = find_dep(deps, ['nsubj', 'nmod:agent', 'csubj'], vi)
        if subdep is not None:
            # if subdep['dep'] != 'nmod:agent':
            si = subdep['dependent'] - 1
            # check relative clause
            if tokens[si]['pos'] in ['WDT', 'WP']:  # which, who, that
                print 'the subject is subcordinate :', subdep
                # find preceding word
                subdep = find_gov(deps, ['acl:relcl'], vi)
                if subdep is None:
                    pass
                else:
                    si = subdep['dependent'] - 1
                    print 'preceding word :', subdep
                    ds = get_descendants(
                        deps, si, preceding_allowing, preceding_filtered
                    )
                    # print ds
                    print 'role :', get_start_end(ds, si)
                    # exit()
            else:
                ds = get_descendants(deps, si, '.*', '(mark)')
            # print ds
            # exit()
            if ds is not None:
                rstart, rend = get_start_end(ds, si)
                if not althead:
                    subjrole = {'role': 'ARG0', 'start': rstart,
                                'end': rend, 'vind': vi}
                else:
                    subjrole = {'role': 'ARG1', 'start': rstart,
                                'end': rend, 'vind': vi}
                labels.append(subjrole)
            else:
                pass
        else:
            if vdep['dep'] == 'xcomp':
                # check passive
                auxdep = find_dep(deps, ['auxpass'], vi)
                if auxdep is not None:
                    pass
                else:
                    pass
                # find subject of govener
                gdep = find_gov(deps, [vdep['dep']], vi)
                assert gdep is not None
                # find subject of govener

        # subdep, org_deptype = find_subject(deps, tokens, vdep, vi)
        # if subdep is not None:
        #     si = subdep['dependent'] - 1
        #     if org_deptype != 'acl:relcl':
        #         ds = get_descendants(deps, si, '.*', '(mark)')
        #     else:
        #         ds = get_descendants(
        #             deps, si, '(det|amod|compound)',
        #             '(punct|acl:relcl|case)')
        #     rstart, rend = get_start_end(ds, si)
        #     print rstart, rend
        #     subjrole = {'role': 'ARG0', 'start': rstart,
        #                 'end': rend, 'vind': vi}
        #     labels.append(subjrole)

            # find arg1: with dep [nobj, nsubjpass]

        # objdeb = find_dep(deps, ['dobj', 'nsubjpass', 'ccomp'], vi)
        # if objdeb is not None:
        #     oi = objdeb['dependent'] - 1
        #     ds = get_descendants(deps, oi, '.*', '^$')
        #     # print ds
        #     rstart, rend = get_start_end(ds, oi)
        #     print rstart, rend
        #     objrole = {'role': 'ARG1', 'start': rstart,
        #                'end': rend, 'vind': vi}
        #     labels.append(objrole)
        #     # exit()
        # else:
        #     if vdep['dep'] == 'xcomp':
        #         # find subject of govener
        #         gdep = find_gov(deps, vdep['dep'], vi)
        #         assert gdep is not None
        #         # find subject of govener
        ds = None
        objdep = find_object(deps, vdep, vi)
        if objdep is not None:
            oi = objdep['dependent'] - 1
            # check relative clause
            if tokens[oi]['pos'] in ['WDT', 'WP']:  # which, who, that
                print 'the object is subcordinate :', objdep
                # find preceding word
                objdep = find_gov(deps, ['acl:relcl'], vi)
                # assert objdep is not None
                if objdep is not None:
                    oi = objdep['dependent'] - 1
                    print 'preceding word :', objdep
                    ds = get_descendants(
                        deps, oi, preceding_allowing, preceding_filtered
                    )
                    # print ds
                    print 'role :', get_start_end(ds, oi)
                    # exit()
            else:
                ds = get_descendants(deps, oi, '.*', '(mark)')

            # print ds
            if ds is not None:
                rstart, rend = get_start_end(ds, oi)
                print rstart, rend
                objrole = {'role': 'ARG1', 'start': rstart,
                           'end': rend, 'vind': vi}
                labels.append(objrole)
            else:
                pass
        else:
            print 'object not found for :', vdep

    return labels


def srl_parse(sentence):
    '''
    @return
        list of role frame list, each frame is a list of semantic roles,
        [VERB, ARG0, ARG1, ...], and each role should specify starting word,
        and ending word
    '''
    if sentence == '':
        print 'Error passed in an empty sentence'
        exit()

    print sentence

    output = nlp.annotate(sentence, properties={
        # 'annotators': 'tokenize,ssplit,pos,depparse,parse',
        'annotators': 'tokenize,pos,ssplit,depparse',
        'outputFormat': 'json'
        # 'outputFormat': 'conllu'
    })

    f = open('log.js', 'w')
    try:
        f.write(json.dumps(output['sentences'][0]['basic-dependencies']))
    except TypeError:
        f.write(output)
        print 'TypeError for sentence :' + sentence
        print output
    f.close

    # Stub, get first verb
    srls = analyze_dep_output(output)

    # print 'predicted srls', srls
    return srls


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: ' + sys.argv[0] + ' <FILE>'
        quit(1)

    f = open(sys.argv[1], 'r')
    text = f.read()

    srl = srl_parse(text)
