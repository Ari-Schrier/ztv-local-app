# gui_launcher.py

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QComboBox, QCalendarWidget, QMessageBox, QSpinBox
)
from PySide6.QtCore import QDate

from daily_chronicle.generator import generate_events_gemini, generate_events_openai
from daily_chronicle.utils_img import generate_image_gemini
from daily_chronicle.utils_img import generate_image_openai
from daily_chronicle.audio_generation import generate_tts_gemini, generate_tts_openai
from daily_chronicle.main import run_pipeline

class LauncherPage(QWidget):
    def __init__(self, on_generate=None):
        super().__init__()
        self.on_generate = on_generate
        self.setWindowTitle("Daily Chronicle Launcher")
        self.setMinimumSize(400, 400)

        layout = QVBoxLayout()

        # Calendar
    
        layout.addWidget(QLabel("Select a date:"))
        self.calendar = QCalendarWidget()
        self.calendar.setSelectedDate(QDate.currentDate())
        layout.addWidget(self.calendar)

        # Number of events spinbox
        layout.addWidget(QLabel("Number of Events:"))
        self.num_events_input = QSpinBox()
        self.num_events_input.setRange(1, 20)
        self.num_events_input.setValue(15)  # Default value
        layout.addWidget(self.num_events_input)

        # Dropdowns
        layout.addWidget(QLabel("Event Generator:"))
        self.event_dropdown = QComboBox()
        self.event_dropdown.addItems(["OpenAI", "Gemini"])
        self.event_dropdown.setCurrentText("OpenAI")
        layout.addWidget(self.event_dropdown)

        layout.addWidget(QLabel("Image Generator:"))
        self.image_dropdown = QComboBox()
        self.image_dropdown.addItems(["OpenAI", "Gemini"])
        self.image_dropdown.setCurrentText("OpenAI")
        layout.addWidget(self.image_dropdown)

        layout.addWidget(QLabel("TTS Generator:"))
        self.tts_dropdown = QComboBox()
        self.tts_dropdown.addItems(["OpenAI", "Gemini"])
        self.tts_dropdown.setCurrentText("OpenAI")
        layout.addWidget(self.tts_dropdown)

        # Launch Button
        launch_button = QPushButton("Generate Video")
        launch_button.clicked.connect(self.launch)
        layout.addWidget(launch_button)

        self.setLayout(layout)

    def launch(self):
        # Get date from calendar
        qdate = self.calendar.selectedDate()
        month = qdate.toString("MMMM")  # e.g., "June"
        day = qdate.day()

        # Map aliases to actual functions
        event_func_map = {
            "OpenAI": generate_events_openai,
            "Gemini": generate_events_gemini,
        }
        image_func_map = {
            "OpenAI": generate_image_openai,
            "Gemini": generate_image_gemini,
        }
        tts_func_map = {
            "OpenAI": generate_tts_openai,
            "Gemini": generate_tts_gemini,
        }

        if self.on_generate:
            self.on_generate(
                month,
                day,
                event_func_map[self.event_dropdown.currentText()],
                image_func_map[self.image_dropdown.currentText()],
                tts_func_map[self.tts_dropdown.currentText()],
            )
        else:
            QMessageBox.critical(self, "Error", "No generation handler connected.")

        def get_num_events(self):
            return self.num_events_input.value()