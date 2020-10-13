from collections import OrderedDict
from typing import Optional, List, Dict
import re

def parse_rst(text: str, names: List[str] = None, extra_roles: List[str] = []) -> OrderedDict:

    snippets = OrderedDict()
    from docutils.core import publish_doctree

    # Sphinx roles
    from docutils.parsers.rst import roles
    from docutils import nodes
    roles.register_generic_role('kbd', nodes.emphasis)
    roles.register_generic_role('ref', nodes.emphasis)

    # custom roles e.g. extlinks
    for role in extra_roles:
        roles.register_generic_role(role, nodes.emphasis)

    doctree = publish_doctree(text)

    def is_literal_block(node):
        return (node.tagname == 'literal_block')

    # TODO: getting lang is tricky, as it's just one of the classes at this point. Another one is 'code', but there can also be user-set classes. Perhaps we should just match against a language array, but this is not optimal. Otherwise we have to do full RST parsing...

    literal_blocks = doctree.traverse(condition=is_literal_block)

    for idx, block in enumerate(literal_blocks):
        snippet = Snippet(block.astext())

        name = ''
        name = ' '.join(block['names'])

        if name != '':
            snippet.meta['name'] = name
            snippets[snippet.meta['name']] = snippet
        else:
            if names and idx < len(names):
                name = names[idx]
                snippet.meta['name'] = name
            else:
                name = 'unnamed'+str(idx)
            snippets[name] = snippet

    return snippets

def parse_markdown(text: str, names: List[str] = None) -> OrderedDict:

    snippets = OrderedDict()
    lines = text.split('\n')

    inside = False
    snippet = Snippet()

    # TODO: fix for indented code blocks e.g. inside lists

    prevl = None
    snippet_lines = []

    for l in lines:
        if l[0:3] == "```":
            if inside:
                # we've found the end of the previous snippet
                snippet.text = '\n'.join(snippet_lines)
                if 'name' in snippet.meta:
                    snippets[snippet.meta['name']] = snippet
                else:
                    snippets['unnamed'+str(len(snippets))] = snippet
                inside = False
            else:
                # we're starting to parse a new snippet
                inside = True
                snippet = Snippet()
                snippet_lines = []
                lang = l[3:].strip()
                if lang != "":
                    snippet.lang = lang
                # look in previous line for metadata in for key1=val1 ; key2=val2
                if prevl is not None:
                    prevl = prevl.strip()
                    if prevl[0:4] == "<!--" and prevl[-3:] == "-->" :
                        prevl = prevl[4:-4]
                        variables = prevl.split(';')
                        for v in variables:
                            split = v.split('=',1)
                            snippet.meta[split[0].strip()] = split[1].strip().strip('"')
        else:
            # store current line into the line buffer
            if inside:
                snippet_lines.append(l)
        # store previous line to be able to look for metadata
        prevl = l
    return snippets

def get_snippets(filename: str, *, names: List[str] = None, extra_roles: List[str] = [], parse: bool = False) -> OrderedDict:
    '''Top level function. Use this one instead of the underlying "parse_rst" etc.'''

    text = open(filename, 'r+', encoding='utf-8').read()
    snippets = None
    if filename.endswith('.rst') or filename.endswith('.rest'):
        snippets = parse_rst(text, names, extra_roles)
    else: # the default is markdown
        snippets = parse_markdown(text, names)
    if parse:
        for s in snippets.values():
            s.commands = parse_snippet(s.text)
    return snippets

from dataclasses import dataclass, field

@dataclass
class Command:
    prompt: str
    command: str
    result: str = ''

@dataclass
class Snippet:
    text: List[str] = field(default_factory=list)
    lang: str = ''
    meta: Dict = field(default_factory=dict)
    commands: List[Command] = field(default_factory=list)

# currently only parse Renode snippets
def parse_snippet(snippet: str) -> List[Command]:
    prompt = re.compile(r'\n(\([a-zA-Z0-9\-]+\) *)([^\n]*)')
    spl = prompt.split('\n'+snippet)
    commands = []
    for i in range(1,len(spl),3):
        commands.append(Command(spl[i].strip(), spl[i+1], spl[i+2]))
    return commands

def autoexec(snippet: Snippet, printer, executor, expector):
    if 'name' in snippet.meta:
        name = snippet.meta['name']
        printer(f"Executing snippet '{name}'")
    else:
        printer(f"Executing unnamed snippet")
    # inject empty command to make sure we have the right prompt
    executor('');
    for c in snippet.commands:
        if c.prompt:
            printer(f"  {c.prompt}")
            assert expector(c.prompt).match is not None
        if c.command:
            printer(f"  >>> {c.command}")
            executor(c.command)
            assert expector(c.command).match is not None
        if c.result:
            for line in c.result.strip().split('\n'):
                printer(f"  {line}")
            assert expector(c.result).match is not None
