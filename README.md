# tuttest

Tuttest is a utility package that simplifies tutorial and example testing.
It provides an interface for extracting code snippets embedded in RST
and Markdown files.

## Features

* `get_snippets` - function to extract snippets from a file. Calls `parse_rst` or `parse_markdown` underneath. Args:

  * `filename` - well, the filename
  * `names` - optional names to give to the extracted snippets, provided as list
  * `extra_roles` - Sphinx or other rst roles which the file might include, so that the parser does not die
  * `parse` - whether to parse the snippet, see below

* `parse_snippet` - parse the snippet into a (prompt, command, result) sequence list. Useful for autoexecuting of docs.

## Getting Started

You can call `tuttest` directly by invoking the `tuttest` command from
the console. This option might be useful for checking tutorials from
i.e., Travis CI script. Here is synopsis of a direct `tuttest` call:

```
  tuttest <file_name> [<snippet_name>]
```
  * `<file_name>` is a file in Markdown or RST format, from which you want
    to extract the code snippets.
  * `<snippet_name>` is a name that you provided for a snippet. Note that
    if you do not name a snippet, it will receive the `unnamedX` name, where
    `X` is the snippet number in the file (starting from 0). Examples of named
    snippets can be found below.

### Examples

This example presents how to use `tuttest` for extracting named and unnamed
code snippets from files. Both the Markdown and RST files used in this
example contain the same code snippets. Therefore, the output produced by
`tuttest` will be the same for both cases.

* `test.rst` (RST format):
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

* `test.md` (Markdown format*)

```
` ``
echo "This is the first unnamed snippet"
` ``

<!-- name="bash-tutorial" -->
` ``
echo "This is a named snippet"
printf "1 + 2 = %d\n" $((1+2))
` ``

` ``
echo "This is the second unnamed snippet"
` ``
```
  \* Note that you have to change the ``` ` `` ``` used in the script to
  `` ``` `` before the first script usage.

Here are ``tuttest`` usage examples. For clarity, these examples are run based on the above RST test document:

* `tuttest test.rst`:
  ```
  echo "This is the first unnamed snippet"
  echo "This is a named snippet"
  printf "1 + 2 = %d\n" 1+2
  echo "This is the second unnamed snippet"
  ```

* `tuttest test.rst bash-tutorial`:
  ```
  echo "This is a named snippet"
  printf "1 + 2 = %d\n" $((1+2))
  ```

* `tuttest test.rst unnamed2`:
  ```
  echo "This is the second unnamed snippet"
  ```

A basic `tuttest` usage in the script might be the following:
```
tuttest test.rst bash-tutorial | bash -
```

## TODOs:

 - [ ] Add support for testing links
