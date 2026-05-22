import re
import subprocess
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from os import environ
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Command:
    prompt: str
    command: str
    result: str = ''


@dataclass
class Snippet:
    text: str = ''
    lang: str = ''
    meta: Dict = field(default_factory=dict)
    commands: List[Command] = field(default_factory=list)
    file: str = ''
    pos: Optional[Tuple[int, int]] = None


def parse_rst(
    text: str, names: Optional[List[str]] = None, extra_roles: List[str] = []
) -> OrderedDict[str, Snippet]:
    snippets = OrderedDict()
    from docutils import nodes
    from docutils.core import publish_doctree

    # Sphinx roles
    from docutils.parsers.rst import roles

    roles.register_generic_role('kbd', nodes.emphasis)
    roles.register_generic_role('ref', nodes.emphasis)

    # Sphinx-tabs extension directives
    from docutils.parsers.rst import directives
    from docutils.parsers.rst.directives.body import Compound

    directives.register_directive('tabs', Compound)
    directives.register_directive('group-tab', Compound)

    # Sphinx jinja extension directives
    from docutils.parsers.rst.directives.body import LineBlock

    jinja = LineBlock
    jinja.option_spec = {'file': str}
    directives.register_directive('jinja', jinja)

    # custom roles e.g. extlinks
    for role in extra_roles:
        roles.register_generic_role(role, nodes.emphasis)

    doctree = publish_doctree(text)

    def is_literal_block(node):
        return node.tagname == 'literal_block'

    # TODO: Getting lang is tricky, as it's just one of the classes at this point.
    #       Another one is 'code', but there can also be user-set classes.
    #       Perhaps we should just match against a language array, but this is not optimal.
    #       Otherwise we have to do full RST parsing...

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
                name = 'unnamed' + str(idx)
            snippets[name] = snippet

        if block.line:
            end = block.line + len(block.astext().strip().splitlines())
            snippet.pos = (block.line, end - 1)

        next_node = next(
            block.findall(include_self=False, descend=False, siblings=True), None
        )
        if next_node is not None and next_node.tagname == 'comment':
            text = next_node.astext()
            if text.strip().startswith('meta:'):
                snippet.meta.update(parse_meta(text.lstrip('meta:')))

    return snippets


def parse_markdown(
    text: str, names: Optional[List[str]] = None
) -> OrderedDict[str, Snippet]:
    snippets = OrderedDict()
    lines = text.split('\n')

    inside = False
    snippet = Snippet()

    # TODO: fix for indented code blocks e.g. inside lists

    prevl = None
    snippet_lines = []

    for i, l in enumerate(lines):
        if l[0:3] == "```":
            if inside:
                # we've found the end of the previous snippet
                snippet.text = '\n'.join(snippet_lines)
                if 'name' in snippet.meta:
                    snippets[snippet.meta['name']] = snippet
                else:
                    snippets['unnamed' + str(len(snippets))] = snippet
                snippet.pos = (block_line, i + 1)
                inside = False
            else:
                # we're starting to parse a new snippet
                inside = True
                snippet = Snippet()
                snippet_lines = []
                block_line = i + 1
                lang = l[3:].strip()
                if lang != "":
                    snippet.lang = lang
                # look in previous line for metadata in for key1=val1 ; key2=val2
                if prevl is not None:
                    prevl = prevl.strip()
                    if prevl[0:4] == "<!--" and prevl[-3:] == "-->":
                        meta = parse_meta(prevl[4:-4])
                        snippet.meta.update(meta)
        else:
            # store current line into the line buffer
            if inside:
                snippet_lines.append(l)
        # store previous line to be able to look for metadata
        prevl = l
    return snippets


def parse_meta(line: str) -> Dict[str, str]:
    meta = dict()
    input = line.lstrip()
    while len(input) > 0:
        key, sep, input = input.partition("=")
        assert len(sep) > 0, f"Unexpected text '{key}' (meta var not found)"
        assert len(key) > 0, f"Empty meta key in '{input}'"

        quote, input = input[0], input[1:]
        assert (
            quote == "'" or quote == '"'
        ), f"Unquoted value for variable '{key}' (expected either `'` or `\"`)"

        val = ""
        while len(input) > 0:
            cmd, _, input = input.partition(";")
            if cmd.rstrip()[-1] == quote:
                val += cmd.rstrip()[:-1]
                break

            val += f"{cmd};"
        else:
            raise AssertionError(
                f"Unterminated meta var '{key}' (closing `{quote}` not found)"
            )

        meta[key] = val

        input = input.lstrip()

    return meta


def get_snippets(
    filename: str,
    *,
    names: Optional[List[str]] = None,
    extra_roles: List[str] = [],
    parse: bool = False,
) -> OrderedDict[str, Snippet]:
    '''Top level function. Use this one instead of the underlying "parse_rst" etc.'''

    text = open(filename, 'r+', encoding='utf-8').read()
    snippets = None
    if filename.endswith('.rst') or filename.endswith('.rest'):
        snippets = parse_rst(text, names, extra_roles)
    else:  # the default is markdown
        snippets = parse_markdown(text, names)
    if parse:
        for s in snippets.values():
            s.commands = parse_snippet(s.text)
    for s in snippets.values():
        s.file = filename

    return snippets


def transform_snippet(
    snippet: Snippet, transformer_cmd: Optional[str | List[str]] = None
) -> Snippet:
    '''Runs the transformer command in a subprocess on a given `Snippet`.'''
    origin = Path(snippet.file)

    env = {
        'TUTTEST_INPUT': snippet.text,
        'TUTTEST_FILE': origin.name,
        'TUTTEST_DIR': origin.absolute().parent,
        'TUTTEST_SNIPPET': snippet.meta.get('name'),
        **environ,
    }

    if transformer_cmd is None:
        if snippet.meta.get("transformer") is None:
            return snippet

        transformer_cmd = str(snippet.meta["transformer"])

    result = subprocess.run(
        transformer_cmd,
        input=snippet.text + '\n',
        cwd=Path(snippet.file).absolute().parent,
        env=env,
        shell=True,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=sys.stdout,
    )

    return Snippet(
        result.stdout,
        snippet.lang,
        snippet.meta,
        snippet.commands,
        snippet.file,
        snippet.pos,
    )


# currently only parse Renode snippets
def parse_snippet(snippet: str) -> List[Command]:
    prompt = re.compile(r'\n(\([a-zA-Z0-9\-]+\) *)([^\n]*)')
    spl = prompt.split('\n' + snippet)
    commands = []
    for i in range(1, len(spl), 3):
        commands.append(Command(spl[i].strip(), spl[i + 1], spl[i + 2]))
    return commands


def autoexec(snippet: Snippet, printer, executor, expector):
    if 'name' in snippet.meta:
        name = snippet.meta['name']
        printer(f"Executing snippet '{name}'")
    else:
        printer(f"Executing unnamed snippet")
    # inject empty command to make sure we have the right prompt
    executor('')
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
