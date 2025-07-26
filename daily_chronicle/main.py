# daily_chronicle/main.py

from daily_chronicle.gui_main_window import MainWindow
import warnings

from PySide6.QtWidgets import QApplication

warnings.filterwarnings("ignore", category=SyntaxWarning)

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    
if __name__ == "__main__":
    main()
