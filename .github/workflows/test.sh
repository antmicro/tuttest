set -e

diff <(tuttest test/test.rst) <(tuttest README.md:test-wholefile)
diff <(tuttest test/test.rst:bash-tutorial) <(tuttest README.md:test-named)
diff <(tuttest test/test.rst:unnamed2) <(tuttest README.md:test-unnamed2)
diff <(tuttest test/test.rst:unnamed2 --prefix-lines-with "docker exec -t test bash -c") <(tuttest README.md:test-prefix)
diff <(tuttest test/test.rst:bash-tutorial,unnamed2 --prefix-lines-with "docker exec -t test bash -c" --single-command) <(tuttest README.md:single-command)

diff <(tuttest test/test.md) <(tuttest README.md:test-wholefile)
diff <(tuttest test/test.md:bash-tutorial) <(tuttest README.md:test-named)
diff <(tuttest test/test.md:unnamed2) <(tuttest README.md:test-unnamed2)
diff <(tuttest test/test.md:unnamed2 --prefix-lines-with "docker exec -t test bash -c") <(tuttest README.md:test-prefix)
diff <(tuttest test/test.md:bash-tutorial,unnamed2 --prefix-lines-with "docker exec -t test bash -c" --single-command) <(tuttest README.md:single-command)

# wildcard testing
diff <(tuttest test/test.md:'unnamed?') <(tuttest test/test.md:unnamed0,unnamed2)
diff <(tuttest test/test.rst:'unnamed?') <(tuttest test/test.rst:unnamed0,unnamed2)
diff <(tuttest test/test-wildcard.md:'[bd]ash*') <(tuttest test/test-wildcard.md:bash-tutorial,dash-tutorial-duplicate)
diff <(tuttest test/test-wildcard.rst:'[bd]ash*') <(tuttest test/test-wildcard.rst:bash-tutorial,dash-tutorial-duplicate)
diff <(tuttest test/test-wildcard.md:'[!d]ash*') <(tuttest test/test-wildcard.md:bash-tutorial)
diff <(tuttest test/test-wildcard.rst:'[!d]ash*') <(tuttest test/test-wildcard.rst:bash-tutorial)

echo "All tests successfully passed!"

