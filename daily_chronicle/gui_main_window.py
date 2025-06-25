# daily_chronicle/main_window.py

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QPlainTextEdit
)
from daily_chronicle.gui_launcher_page import LauncherPage
from daily_chronicle.main import run_pipeline
from daily_chronicle.pipeline import generate_and_save_events, initialize_pipeline

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Chronicle")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)  # User can still resize

        # --- Logger setup
        self.logger = self.log

        # --- Console panel (always visible at bottom)
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlaceholderText("Logs will appear here...")

        # --- Stacked widget for app pages
        self.pages = QStackedWidget()

        # --- Add launcher page
        self.launcher_page = LauncherPage(on_generate=self.run_full_pipeline)
        self.pages.addWidget(self.launcher_page)

        # --- Layout
        layout = QVBoxLayout()
        layout.addWidget(self.pages)
        layout.addWidget(self.console)
        self.setLayout(layout)

    def log(self, message: str):
        self.console.appendPlainText(message)

    def run_full_pipeline(self, month, day, event_func, image_func, tts_func):
        
        initialize_pipeline(self.logger)

        num_events = self.launcher_page.get_num_events()

        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # STEP 2
        events, event_json_path = generate_and_save_events(
            month, day, event_func, output_dir, self.logger, num_events
        )

        if not events:
            return  # Early exit if event generation failed

        # Next: Launch EventReviewPage, save reviewed events, and continue pipeline...

        run_pipeline(
            month=month,
            day=day,
            chosen_event_func=event_func,
            chosen_img_func=image_func,
            chosen_tts_func=tts_func,
            logger=self.log
        )
        self.log("🎬 Generation complete.")

        # TODO: Once we build EventReviewPage, we can swap to it here:
        # self.pages.setCurrentWidget(self.event_review_page)
