# tuttest

Copyright (c) 2020-2022 [Antmicro](https://www.antmicro.com)

Tuttest is a simple utility which lets you easily test tutorials and examples and reuse code between e.g. READMEs and other parts of your project.
It provides an interface for extracting code snippets (code blocks) embedded in RST and Markdown files.

## CLI usage

You can call `tuttest` directly by invoking the `tuttest` command from the console.
This option might be useful for checking tutorials from i.e. a GitHub Actions script.
Here is what a direct `tuttest` call looks like:

```
tuttest <file_name> [<snippet_name>] [--prefix-lines-with <prefix>] [--single-command]
```

* `<file_name>`: file in Markdown or RST from which you want to extract the code snippets.
* `[<snippet_name>]`: if absent, extract all the snippets. If present, this is the name of the snippet
  (or snippets, with names separated by `,`) that you want to extract.
  Note that unnamed snippets can still be referred to as `unnamedX`, where `X`
  is the snippet's order in the file (starting from 0). See [naming snippets](#naming-snippets).

### Optional flags

* `--prefix-lines-with`: add whatever command you provide as `<prefix>` at the beginning of the snippet
* `--single-command`: if provided, all snippets from `<snippet_name>` (if specified) will be
  packed into a one-liner, separated with `;`.
* `--language`: if provided, filter out snippets for a specified `<lang>` language.
* `--enable-transformers`: if provided, enable [snippet transformer](#snippet-transformers) execution
  for snippets that specify one.

## Programmatic use

* `get_snippets` - function to extract snippets from a file. Calls `parse_rst` or `parse_markdown` underneath. Args:

  * `filename` - well, the filename
  * `names` - optional names to give to the extracted snippets, provided as list
  * `extra_roles` - Sphinx or other rst roles which the file might include, so that the parser does not die
  * `parse` - whether to parse the snippet, see below

* `transform_snippet` - run the snippet through a transformation command. Returns transformed snippet. Args:
  
  * `snippet` - target snippet
  * `transform_cmd` - optional transformation command. If provided, will override the transformer stored in snippet metadata.

* `parse_snippet` - parse the snippet into a (prompt, command, result) sequence list. Useful for autoexecuting of docs.

## Metadata

`tuttest` allows you to attach additional information to a snippet in a form of key-value pairs called metadata.
The basic syntax for metadata is as follows:

````md
<!-- key1="value1"; key2="value2" -->
```sh
echo "Sample markdown snippet"
```
````

````rst
.. code-block:: sh

   echo "Sample rst snippet"

..
   meta: key1="value1"; key2="value2"
````

Each pair takes the form of `key="value"`. Subsequent values are separated with `;`.

The metadata is accessible through the `Snippet.meta` property:

```py
from tuttest import get_snippets

for snip in get_snippets('path/to/file/md').values():
  print(snip.meta)
```

You can use this mechanism to implement specialized logic targeted specifically for your use case.
For example, you could provide platform-specific snippets in your documentation
and then filter them out in testing based on the platform of the testing environment:

````md
<!-- target="linux" -->
```sh
cat /etc/os-release
```

<!-- target="windows" -->
```sh
ver
```
````

```py
import sys
from tuttest import get_snippets

for snip in get_snippets('path/to/file.md').values():
  if snip.meta.get('target') == sys.name:
    run_snippet(snip)
```

`tuttest` makes use of this mechanism to provide additional functionality using specialized keys:

### Naming snippets

By default, `tuttest` extracts all snippets from a given file.
In addition, specific snippet can only be accessed by iterating over all of them.

To fix both of these problems, `tuttest` provides a way to name individual snippets
using the `name` keyword:

````md
<!-- name="my_snippet" -->
```sh
echo hello
```

<!-- name="my_snippet2" -->
```sh
echo hello2
```
````

You can specify which snippets you want returned by providing `tuttest` with list of target names.
Both cli and library usages are supported:

```sh
tuttest path/to/readme.md my_snippet
```

```py
from tuttest import get_snippets

snip = get_snippets('path/to/readme.md', names=['my_snippet'])
```

In addition, named snippets can be accessed directly using their name:

```py
from tuttest import get_snippets

snip = get_snippets('path/to/readme.md')

my_snippet = snip['my_snippet']
```

### Snippet transformers

Sometimes, you might want to slightly modify snippet contents, depending on execution context.

For example, in normal case, your build instructions would point the end user to use the default branch:

````md
<!-- name="fetch-repo" -->
```sh
git clone https://github.com/your/repo.git
```
...
````

The issue with this approach is that this snippet would always end up fetching the default branch,
even when you were making changes on a different branch.
This is especially important if you wanted to use `tuttest` in CI tests, since instead of testing your changes,
they would keep running off of the default branch.

To fix this problem, `tuttest` allows you to specify a snippet transformer using the `transformer` keyword:

````md
<!-- name="fetch-repo"; transformer="echo $TUTTEST_INPUT --branch $(git branch --show-current)" -->
```sh
git clone https://github.com/your/repo.git
```
...
````

By default, `tuttest` ignores all transformers as it's primary usage is to test documentation examples as it.
To enable snippet transformers, you have to explicitly opt-in into their usage,
either by calling `tuttest` with the `--enable-transformers` flag or by passing
a snippet returned from `get_snippets` through `transform_snippet`,
depending on whether you're using `tuttest` from cli or as a library.

`tuttest` passes the original contents of the snippet to a transformer on standard input.
The transformers job is to produce an updated snippet on standard output.

Transformers are executed as if they were called from your shell,
meaning that you can use any command or chain of commands to to act as a transformer.

The working directory for transformer execution is set to the parent directory of the file the original snippet is from.
If the transformer command is a relative path, it will be resolved relative to this directory.

In addition to original snippet contents, the transformer is passed additional information as environment variables:

* `TUTTEST_INPUT` - contains original snippet contents. Useful in simpler cases, like appending text
* `TUTTEST_FILE` - file name of the file the snippet is from
* `TUTTEST_DIR` - the working directory set for the current transformer
* `TUTTEST_SNIPPET` - contains snippet name for the snippet currently being transformed.

## Examples

This example presents how to use `tuttest` for extracting named and unnamed code snippets from files.
Both the Markdown and RST files used in this example contain the same code snippets.
Therefore, the output produced by `tuttest` should be the same for both cases.

* `test.rst` (reStructuredText):

```
.. code-block:: bash

   echo "This is the first unnamed snippet"
  
.. code-block:: bash

   echo "This is a named snippet"
   printf "1 + 2 = %d\n" $((1+2))

..
  meta: name="bash-tutorial"

.. code-block:: bash

   echo "This is the second unnamed snippet"
```

* `test.md` (Markdown)

````
```
echo "This is the first unnamed snippet"
```

<!-- name="bash-tutorial" -->
```
echo "This is a named snippet"
printf "1 + 2 = %d\n" $((1+2))
```

```
echo "This is the second unnamed snippet"
```
````

Here are some `tuttest` usage examples.
For clarity, these examples are run based on the above RST test document:

* `tuttest test/test.rst`:
<!-- name="test-wholefile" -->
```
echo "This is the first unnamed snippet"

echo "This is a named snippet"
printf "1 + 2 = %d\n" $((1+2))

echo "This is the second unnamed snippet"
```

* `tuttest test/test.rst bash-tutorial`:
<!-- name="test-named" -->
```
echo "This is a named snippet"
printf "1 + 2 = %d\n" $((1+2))
```

* `tuttest test/test.rst unnamed2`:
<!-- name="test-unnamed2" -->
```
echo "This is the second unnamed snippet"
```

* `tuttest test/test.rst unnamed2 --prefix-lines-with "docker exec -t test bash -c"`
<!-- name="test-prefix" -->
```
docker exec -t test bash -c 'echo "This is the second unnamed snippet";'
```

* `tuttest test/test.rst bash-tutorial,unnamed2 --prefix-lines-with "docker exec -t test bash -c" --single-command`
<!-- name="single-command" -->
```
docker exec -t test bash -c 'echo "This is a named snippet";printf "1 + 2 = %d\n" $((1+2));echo "This is the second unnamed snippet";'
```

By default, `tuttest` extracts the snippets but does not execute them.
To actually execute a snippet, you can e.g. pipe the results to bash like:
```
# this executes the snippet called bash-tutorial from test.rst in bash
tuttest test.rst bash-tutorial | bash -
```

## License

[Apache 2.0](LICENSE)
