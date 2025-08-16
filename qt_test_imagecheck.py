# qt_test_imagecheck.py
# Usage:
#   ./.venv/bin/python qt_test_imagecheck.py
# Optional (verbose plugin logging):
#   QT_DEBUG_PLUGINS=1 ./.venv/bin/python qt_test_imagecheck.py

import os
import sys
from pathlib import Path

# --- Optional: turn on verbose plugin loading logs ---
if os.environ.get("QT_DEBUG_PLUGINS") is None:
    # leave it off by default; enable by prefixing the command with QT_DEBUG_PLUGINS=1
    pass

from PySide6.QtCore import QLibraryInfo, QCoreApplication
from PySide6.QtGui import QImageReader

def main():
    # 1) Show where Qt *thinks* plugins live
    plugins_path = QLibraryInfo.path(QLibraryInfo.PluginsPath)
    print(f"🧩 Qt Plugins Path (QLibraryInfo): {plugins_path}")

    # Show current library search paths
    print("📚 Library paths (before):")
    for p in QCoreApplication.libraryPaths():
        print("   -", p)

    # 2) First part of hardening: explicitly add the plugins path
    QCoreApplication.addLibraryPath(plugins_path)

    print("📚 Library paths (after addLibraryPath):")
    for p in QCoreApplication.libraryPaths():
        print("   -", p)

    # 1) Supported formats check
    fmts = sorted(bytes(f).decode() for f in QImageReader.supportedImageFormats())
    print(f"🖼️ Supported image formats ({len(fmts)}): {fmts}")

    # helpful context
    print(f"📂 CWD: {Path.cwd()}")
    print(f"🐍 Python: {sys.version.split()[0]} | PySide6 OK")

if __name__ == "__main__":
    main()
