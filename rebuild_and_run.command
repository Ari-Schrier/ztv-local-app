#!/bin/bash
# =====================================================
# rebuild_and_run.command
# Tear down the venv, rebuild it from scratch, 
# install deps, and launch the app in a clean state.
# =====================================================

# Bash strict mode
set -euo pipefail
# -e : exit immediately on error
# -u : error on undefined variables
# -o pipefail : pipeline fails if any component fails

# Add timestamps to command trace
export PS4='+ $(date "+%H:%M:%S") '
set -x

# Ensure we run from the folder where this script lives
cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")"

# Select Python interpreter
# Hard-pin Homebrew Python 3.13 (your known environment)
# Fallback to system python3 if not present
PYTHON_BIN="/opt/homebrew/opt/python@3.13/bin/python3.13"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Homebrew Python 3.13 not found; falling back to \`python3\`."
  PYTHON_BIN="$(command -v python3)"
fi

# Rebuild the virtual environment
echo "🔄 Rebuilding virtual environment..."
rm -rf .venv
"$PYTHON_BIN" -m venv .venv
VENV_PY="./.venv/bin/python"

# Install dependencies
echo "📦 Installing dependencies..."
"$VENV_PY" -m pip install -U pip wheel setuptools

# Use a local cache if available (fast / offline)
if [ -d rebuild_cache ]; then
  "$VENV_PY" -m pip install --no-index --find-links ./rebuild_cache -r requirements-trial.lock
else
  "$VENV_PY" -m pip install -r requirements-trial.lock
fi

# Clean up environment variables that can pollute Qt/Python
unset QT_PLUGIN_PATH QT_QPA_PLATFORM_PLUGIN_PATH
unset DYLD_FRAMEWORK_PATH DYLD_LIBRARY_PATH
export PYTHONNOUSERSITE=1   # disable user site-packages (~/.local, ~/Library/Python)

# Dynamically point Qt to THIS venv’s platform plugins
export QT_QPA_PLATFORM_PLUGIN_PATH="$(
"$VENV_PY" - <<'PY'
import sysconfig, pathlib
print(pathlib.Path(sysconfig.get_paths()["purelib"]) / "PySide6/Qt/plugins/platforms")
PY
)"

# Diagnostics
echo "✅ Python: $("$VENV_PY" -V)"
echo "✅ Venv:   $VENV_PY"
echo "✅ Qt platforms: $QT_QPA_PLATFORM_PLUGIN_PATH"

# Run in isolated mode
# -I : ignores PYTHON* env vars, disables user site-packages
# Add repo root to sys.path manually since -I disables it
echo "Launching Daily Chronicle..."
exec "$VENV_PY" -I - <<'PY'
import runpy, sys
sys.path.insert(0, ".")  # ensure repo root is importable
runpy.run_module("daily_chronicle.main", run_name="__main__")
PY
