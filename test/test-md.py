#!/usr/bin/env python3

import sys
sys.path.insert(0,'..')

from tuttest import get_snippets

s = get_snippets('snippets.md')

# make sure we indeed have 5 snippets
assert len(s) == 5

# execute one of them and see if the output is OK
import subprocess
output=subprocess.getoutput(s['second'].text)
assert output == s['second-result'].text

# see if we have correct metadata for another one
assert s['fifth'].meta['comment'] == 'something'

print("All tests passed!")
