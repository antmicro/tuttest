from collections import OrderedDict
from typing import OrderedDict

def parse_rst(text: str) -> OrderedDict:

    snippets = OrderedDict()
    from docutils.core import publish_doctree, publish_from_doctree
    doctree = publish_doctree(text)

    def is_literal_block(node):
        return (node.tagname == 'literal_block')

    # TODO: getting lang is tricky, as it's just one of the classes at this point. Another one is 'code', but there can also be user-set classes. Perhaps we should just match against a language array, but this is not optimal. Otherwise we have to do full RST parsing...

    literal_blocks = doctree.traverse(condition=is_literal_block)
    for block in literal_blocks:
        snippet = {'text': block.astext(), 'lang': '', 'meta': {}}
        name = ' '.join(block['names'])
        if name != '':
            snippet['meta']['name'] = name
            snippets[snippet['meta']['name']] = snippet
        else:
            snippets['unnamed'+str(len(snippets))] = snippet

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


def get_snippets(filename: str) -> OrderedDict:

    text = open(filename).read()
    snippets = None
    if filename.endswith('.rst') or filename.endswith('.rest'):
        snippets = parse_rst(text)
    else: # the default is markdown
        snippets = parse_markdown(text)
    return snippets
