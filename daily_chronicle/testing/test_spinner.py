from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QMovie
import sys

class SpinnerTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spinner Test")
        self.setMinimumSize(400, 300)

        # Spinner setup
        self.spinner_label = QLabel(self)
        self.spinner_movie = QMovie("resources/progress_spinner.gif")  # <-- Use a valid GIF path here
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_label.setFixedSize(100, 100)
        self.spinner_label.setStyleSheet("background-color: rgba(255, 255, 255, 180); border-radius: 8px;")
        self.spinner_label.hide()

        # Button to toggle spinner
        self.button = QPushButton("Start Spinner")
        self.button.clicked.connect(self.start_spinner)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.button, alignment=Qt.AlignCenter)
        layout.addWidget(self.spinner_label, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def start_spinner(self):
        self.spinner_label.show()
        self.spinner_movie.start()
        self.button.setEnabled(False)

        # Stop after 3 seconds (simulate task)
        QTimer.singleShot(3000, self.stop_spinner)

    def stop_spinner(self):
        self.spinner_movie.stop()
        self.spinner_label.hide()
        self.button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpinnerTestWindow()
    window.show()
    sys.exit(app.exec())
