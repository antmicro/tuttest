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
  is the snippet's order in the file (starting from 0). See examples below.

### Optional flags

* `--prefix-lines-with`: add whatever command you provide as `<prefix>` at the beginning of the snippet
* `--single-command`: if provided, all snippets from `<snippet_name>` (if specified) will be
  packed into a one-liner, separated with `;`.

## Programmatic use

* `get_snippets` - function to extract snippets from a file. Calls `parse_rst` or `parse_markdown` underneath. Args:

  * `filename` - well, the filename
  * `names` - optional names to give to the extracted snippets, provided as list
  * `extra_roles` - Sphinx or other rst roles which the file might include, so that the parser does not die
  * `parse` - whether to parse the snippet, see below

* `parse_snippet` - parse the snippet into a (prompt, command, result) sequence list. Useful for autoexecuting of docs.

### Naming snippets externally

The `names` argument helps in the Pythonic use of `tuttest` - whenever you can't or don't want to change the documentation you want to test by naming snippets inside the docs, but you still want to keep some structure, you might want to sue this feature to name snippets extracted from a doc. An example below:

```
names = ['first_name', 'some_other_name', 'and_yet_another'] 
s = get_snippets('path/to/file.rst', names=names)
print(s['first_name'])
# prints the snippet text of the first snippet found in the file
```

Of course this way you will rely on the order of the snippets, but perhaps this is not a bad thing.

## Examples

This example presents how to use `tuttest` for extracting named and unnamed code snippets from files.
Both the Markdown and RST files used in this example contain the same code snippets.
Therefore, the output produced by `tuttest` should be the same for both cases.

* `test.rst` (reStructuredText):

```
.. code-block:: bash

   echo "This is the first unnamed snippet"
  
.. code-block:: bash
   :name: bash-tutorial

   echo "This is a named snippet"
   printf "1 + 2 = %d\n" $((1+2))

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
