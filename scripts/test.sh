#! /bin/bash

# Get base directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
BASE="$( realpath $DIR/..)"

echo "Testscript, basedir is: ${BASE}"
