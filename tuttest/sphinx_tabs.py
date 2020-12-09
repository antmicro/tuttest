from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.parsers.rst.roles import set_classes
from docutils.parsers.rst.directives.body import Compound

"""
Classes used for handling sphinx_tabs extension directives in tuttest.

See: https://github.com/executablebooks/sphinx-tabs
"""


class Tabs(Compound):
    """Class used for tabs directive"""
    pass


class GroupTab(Directive):
    """Class used for group-tab directive"""

    has_content = True
    optional_arguments = 1
    option_spec = {'class': directives.class_option,
                   'name': directives.unchanged}

    def run(self):
        self.assert_has_content()
        set_classes(self.options)
        text = '\n'.join(self.content)
        text_nodes, messages = self.state.inline_text(text, self.lineno)
        node = nodes.literal_block(text, '', *text_nodes, **self.options)
        node.line = self.content_offset + 1
        self.add_name(node)
        return [node] + messages
