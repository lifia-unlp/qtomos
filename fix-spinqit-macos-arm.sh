#!/usr/bin/env bash
set -e

SO_FILE=".venv/lib/python3.8/site-packages/spinqit/spinq_backends.cpython-38-darwin.so"

install_name_tool -rpath '$ORIGIN' '@loader_path' "$SO_FILE"

codesign --force --sign - "$SO_FILE"

otool -l "$SO_FILE" | grep -A2 LC_RPATH