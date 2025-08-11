# tools/test_placeholder_load_gui.py
from pathlib import Path
from PySide6.QtGui import QGuiApplication, QPixmap, QImageReader

PLACEHOLDER = Path("resources/image_fail_placeholder.jpg")

def main():
    print("CWD:", Path.cwd())
    print("Placeholder path:", PLACEHOLDER.resolve())
    print("Exists?:", PLACEHOLDER.exists())
    if not PLACEHOLDER.exists():
        return

    try:
        size = PLACEHOLDER.stat().st_size
    except Exception as e:
        size = f"Error reading size: {e}"
    print("File size:", size, "bytes")

    # Spin up the minimal GUI context required for QPixmap
    app = QGuiApplication([])

    # Try QPixmap
    pm = QPixmap(str(PLACEHOLDER))
    print("QPixmap loaded?:", not pm.isNull())

    # Also try QImageReader so we can see an error string if it fails
    reader = QImageReader(str(PLACEHOLDER))
    ok = reader.canRead()
    print("QImageReader canRead?:", ok)
    if not ok:
        print("QImageReader error:", reader.errorString())

if __name__ == "__main__":
    main()
