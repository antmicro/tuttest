set -e

diff <(tuttest test/test.rst) <(tuttest README.md test-wholefile)
diff <(tuttest test/test.rst bash-tutorial) <(tuttest README.md test-named)
diff <(tuttest test/test.rst unnamed2) <(tuttest README.md test-unnamed2)
diff <(tuttest test/test.rst unnamed2 --prefix-lines-with "docker exec -t test bash -c") <(tuttest README.md test-prefix)

diff <(tuttest test/test.md) <(tuttest README.md test-wholefile)
diff <(tuttest test/test.md bash-tutorial) <(tuttest README.md test-named)
diff <(tuttest test/test.md unnamed2) <(tuttest README.md test-unnamed2)
diff <(tuttest test/test.md unnamed2 --prefix-lines-with "docker exec -t test bash -c") <(tuttest README.md test-prefix)
