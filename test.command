#!/bin/bash
set -e

# Always open in a new Terminal tab/window
# Get the directory of this script and cd to repo root
cd "$(cd -- "$(dirname -- "$0")" && pwd)"
echo "📂 Repo root: $(pwd)"

# Check that venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment (.venv) not found."
    exit 1
fi

# Use venv python
PY_BIN="./.venv/bin/python"

if [ ! -x "$PY_BIN" ]; then
    echo "❌ Python binary not found in .venv."
    exit 1
fi

echo "🐍 Using Python: $($PY_BIN -V)"

echo
echo "=== 🧩 Running qt_test_imagecheck.py (JPEG plugin check) ==="
$PY_BIN qt_test_imagecheck.py || echo "⚠️ qt_test_imagecheck.py exited with error"

echo
echo "=== 🖼️ Running qt_test_placeholder.py (placeholder load test) ==="
$PY_BIN qt_test_placeholder.py || echo "⚠️ qt_test_placeholder.py exited with error"

echo
echo "✅ Tests complete. Output above."
echo "Press Enter to close..."
read
