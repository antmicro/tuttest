from collections import OrderedDict
from typing import OrderedDict

def parse_rst(text: str) -> OrderedDict:

    snippets = OrderedDict()
    from docutils.core import publish_doctree, publish_from_doctree
    tree = publish_doctree(text)

    # TODO: extract the snippets from rst tree

    return snippets

def parse_markdown(text: str) -> OrderedDict:

    snippets = OrderedDict()
    lines = text.split('\n')

    inside = False
    snippet = {'text': '', 'lang': '', 'meta': {}}

    # TODO: fix for indented code blocks e.g. inside lists

    prevl = None
    snippet_lines = []

    for l in lines:
        if l[0:3] == "```":
            if inside:
                # we've found the end of the previous snippet
                snippet['text'] = '\n'.join(snippet_lines)
                if 'name' in snippet['meta']:
                    snippets[snippet['meta']['name']] = snippet
                else:
                    snippets['unnamed'+str(len(snippets))] = snippet
                inside = False
            else:
                # we're starting to parse a new snippet
                inside = True
                snippet = {'text': '', 'lang': '', 'meta': {}}
                snippet_lines = []
                lang = l[3:].strip()
                if lang != "":
                    snippet['meta']['lang'] = lang
                # look in previous line for metadata in for key1=val1 ; key2=val2
                if prevl is not None:
                    prevl = prevl.strip()
                    if prevl[0:4] == "<!--" and prevl[-3:] == "-->" :
                        prevl = prevl[4:-4]
                        variables = prevl.split(';')
                        for v in variables:
                            split = v.split('=',1)
                            snippet['meta'][split[0].strip()] = split[1].strip().strip('"')
        else:
            # store current line into the line buffer
            if inside:
                snippet_lines.append(l)
        # store previous line to be able to look for metadata
        prevl = l
    return snippets


def get_snippets(filename: str, syntax = 'markdown') -> OrderedDict:

    text = open(filename).read()
    snippets = None
    if syntax == 'markdown':
        snippets = parse_markdown(text)
    elif syntax == 'rst':
        spippets = parse_rst(text)
    return snippets
