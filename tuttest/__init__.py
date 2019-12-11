from collections import OrderedDict

def get_snippets(filename):

    snippets = OrderedDict()
    lines = open(filename).readlines()

    inside = False
    snippet = {'text': '', 'lang': '', 'meta': {}}

    prevl = None
    for l in lines:
        if l[0:3] == "```":
            if inside:
                if 'name' in snippet['meta']:
                    snippets[snippet['meta']['name']] = snippet
                else:
                    snippets['unnamed'+str(len(snippets))] = snippet
                inside = False
                snippet = {'text': '', 'lang': '', 'meta': {}}
            else:
                inside = True
                lang = l[3:].strip()
                if lang != "":
                    snippet['meta']['lang'] = lang
                if prevl is not None:
                    prevl = prevl.strip()
                    if prevl[0:4] == "<!--" and prevl[-3:] == "-->" :
                        prevl = prevl[4:-4]
                        variables = prevl.split(';')
                        for v in variables:
                            split = v.split('=',1)
                            snippet['meta'][split[0].strip()] = split[1].strip().strip('"')
        else:
            if inside:
                snippet['text'] += l
        prevl = l
    return snippets

