# event_review.py

import sys
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QMessageBox, QFormLayout, QSizePolicy
)

class EventReviewWindow(QWidget):
    def __init__(self, json_path: Path):
        super().__init__()

        self.json_path = json_path
        self.events = self.load_events()
        self.index = 0

        self.init_ui()
        self.update_display()

    def load_events(self):
        with self.json_path.open("r") as f:
            data = json.load(f)
        if isinstance(data, list) and all(isinstance(event, dict) for event in data):
            return data
        else:
            raise ValueError("Invalid JSON structure — expected flat list of event dicts.")

    def save_events(self):
        with self.json_path.open("w") as f:
            json.dump(self.events, f, indent=2)

    def init_ui(self):
        self.setWindowTitle("Daily Chronicle — Event Review")
        self.setFixedSize(750, 700)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)  # Set nice margins

        instructions = QLabel(
            "Instructions:\n"
            "- Review each event.\n"
            "- You may edit Header Title, Description, Details, Image Prompt, and Audio Text.\n"
            "- 'Previous' and 'Next' navigate events.\n"
            "- 'Reject Event' removes an event.\n"
            "- 'Save and Close' saves the JSON and closes this window.\n"
        )
        instructions.setWordWrap(True)
        instructions.setFixedWidth(700)
        instructions.setMaximumHeight(130)
        main_layout.addWidget(instructions)


        # Counter label
        self.counter_label = QLabel("")
        main_layout.addWidget(self.counter_label)

        # Form layout for fields
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)

        self.date_string_input = QLineEdit()
        self.date_string_input.setReadOnly(True)
        form_layout.addRow("Date:", self.date_string_input)

        self.header_title_input = QTextEdit()
        self.header_title_input.setMinimumWidth(600)
        self.header_title_input.setFixedHeight(50)
        form_layout.addRow("Header Title:", self.header_title_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMinimumWidth(600)
        self.description_input.setFixedHeight(50)
        form_layout.addRow("Description:", self.description_input)

        self.detail_1_input = QTextEdit()
        self.detail_1_input.setMinimumWidth(600)
        self.detail_1_input.setFixedHeight(50)
        form_layout.addRow("Detail 1:", self.detail_1_input)

        self.detail_2_input = QTextEdit()
        self.detail_2_input.setMinimumWidth(600)
        self.detail_2_input.setFixedHeight(50)
        form_layout.addRow("Detail 2:", self.detail_2_input)

        self.image_prompt_input = QTextEdit()
        self.image_prompt_input.setMinimumWidth(600)
        self.image_prompt_input.setFixedHeight(75)
        form_layout.addRow("Image Prompt:", self.image_prompt_input)

        self.audio_text_input = QTextEdit()
        self.audio_text_input.setMinimumWidth(600)
        self.audio_text_input.setMaximumHeight(100)
        form_layout.addRow("Audio Text:", self.audio_text_input)

        main_layout.addLayout(form_layout)

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.on_prev)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.on_next)
        nav_layout.addWidget(self.next_button)

        self.reject_button = QPushButton("Reject Event")
        self.reject_button.clicked.connect(self.on_reject)
        nav_layout.addWidget(self.reject_button)

        self.save_exit_button = QPushButton("Save and Close")
        self.save_exit_button.clicked.connect(self.on_save_and_exit)
        nav_layout.addWidget(self.save_exit_button)

        main_layout.addLayout(nav_layout)

        self.setLayout(main_layout)

    def update_display(self):
        if not self.events:
            self.counter_label.setText("Event 0 of 0")
            self.clear_fields()
            return

        event = self.events[self.index]
        self.counter_label.setText(f"Event {self.index + 1} of {len(self.events)}")

        # Populate fields
        self.date_string_input.setText(event.get("date_string", ""))
        self.header_title_input.setPlainText(event.get("header_title", ""))
        self.description_input.setPlainText(event.get("description", ""))
        self.detail_1_input.setPlainText(event.get("detail_1", ""))
        self.detail_2_input.setPlainText(event.get("detail_2", ""))
        self.image_prompt_input.setPlainText(event.get("image_prompt", ""))
        self.audio_text_input.setPlainText(event.get("audio_text", ""))

        # Enable/disable nav buttons
        self.prev_button.setEnabled(self.index > 0)
        self.next_button.setEnabled(self.index < len(self.events) - 1)

    def save_current_event(self):
        event = {
            "date_string": self.date_string_input.text(),
            "header_title": self.header_title_input.toPlainText(),
            "description": self.description_input.toPlainText(),
            "detail_1": self.detail_1_input.toPlainText(),
            "detail_2": self.detail_2_input.toPlainText(),
            "image_prompt": self.image_prompt_input.toPlainText(),
            "audio_text": self.audio_text_input.toPlainText()
        }
        self.events[self.index] = event

    def clear_fields(self):
        self.date_string_input.clear()
        self.header_title_input.clear()
        self.description_input.clear()
        self.detail_1_input.clear()
        self.detail_2_input.clear()
        self.image_prompt_input.clear()
        self.audio_text_input.clear()

    def on_prev(self):
        self.save_current_event()
        self.index -= 1
        self.update_display()

    def on_next(self):
        self.save_current_event()
        self.index += 1
        self.update_display()

    def on_reject(self):
        if not self.events:
            return
        self.save_current_event()
        confirm = QMessageBox.question(
            self, "Confirm Reject", "Are you sure you want to reject this event?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            del self.events[self.index]
            if self.index >= len(self.events):
                self.index = max(0, len(self.events) - 1)
            self.update_display()

    def on_save_and_exit(self):
        self.save_current_event()
        self.save_events()
        QMessageBox.information(self, "Saved", "✅ Events saved.")
        self.close()

# Test main launcher
if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_file_path = Path(__file__).parent / "testing" / "June_19_events.json"
    window = EventReviewWindow(test_file_path)
    window.show()
    sys.exit(app.exec())
