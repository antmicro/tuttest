# tuttest

A tutorial tester script. Extract the code blocks (TODO: also links) from tutorial and see if, when followed, the tutorial actually works.

## Features

* `get_snippets` - function to extract snippets from a file. Calls `parse_rst` or `parse_markdown` underneath. Args:

  * `filename` - well, the filename
  * `names` - optional names to give to the extracted snippets, provided as list
  * `extra_roles` - Sphinx or other rst roles which the file might include, so that the parser does not die
  * `parse` - whether to parse the snippet, see below
  
* `parse_snippet` - parse the snippet into a (prompt, command, result) sequence list. Useful for autoexecuting of docs.
