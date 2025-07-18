# daily_chronicle/main_window.py

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QPlainTextEdit, QLabel, QMessageBox
)
from PySide6.QtCore import Signal, Slot, QThreadPool, Qt
from PySide6.QtGui import QMovie
from daily_chronicle.utils_threading import WorkerRunnable
from daily_chronicle.gui_event_review_page import EventReviewPage
from daily_chronicle.gui_image_review_page import ImageReviewPage
from daily_chronicle.gui_launcher_page import LauncherPage
from daily_chronicle.pipeline import build_video_segments, cleanup, export_final_output, generate_and_save_events, generate_assets_threaded, initialize_pipeline, load_reviewed_assets, load_reviewed_events
from daily_chronicle.utils_logging import emoji
from daily_chronicle.utils_video import reveal_video_in_file_browser

class MainWindow(QWidget):
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Chronicle")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)  # User can still resize


                # Spinner setup
        self.spinner_label = QLabel(self)
        self.spinner_movie = QMovie("resources/progress_spinner.gif")
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_label.setFixedSize(100, 100)
        self.spinner_label.setStyleSheet("background-color: rgba(255, 255, 255, 180); border-radius: 8px;")
        self.spinner_label.hide()

        # Center the spinner manually (updates on resize)
        self.resizeEvent = self.center_spinner

        # --- Console panel (always visible at bottom)
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlaceholderText("Logs will appear here...")

        # --- Stacked widget for app pages
        self.pages = QStackedWidget()

        # --- Add launcher page
        self.launcher_page = LauncherPage(on_generate=self.start_event_phase)
        self.pages.addWidget(self.launcher_page)

        # --- Layout
        layout = QVBoxLayout()
        layout.addWidget(self.pages)
        layout.addWidget(self.console)
        self.setLayout(layout)

        # --- Connect signal to slot
        self.log_signal.connect(self.append_log)

        # --- Assign logger function
        self.logger = self.get_logger()

        self.thread_pool = QThreadPool()

    def center_spinner(self, event=None):
        # Center the spinner in the MainWindow
        w, h = self.spinner_label.width(), self.spinner_label.height()
        x = (self.width() - w) // 2
        y = (self.height() - h) // 2
        self.spinner_label.move(x, y)
        if event:
            super().resizeEvent(event)

    def show_spinner(self):
        self.spinner_movie.start()
        self.spinner_label.show()
        self.spinner_label.raise_()

    def hide_spinner(self):
        self.spinner_movie.stop()
        self.spinner_label.hide()

    def get_logger(self):
        return lambda msg: self.log_signal.emit(msg)
    
    @Slot(str)
    def append_log(self, message: str):
        self.console.appendPlainText(message)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def start_event_phase(self, month, day, event_func, img_func, tts_func):
        
        initialize_pipeline(self.logger)

        num_events = self.launcher_page.get_num_events()
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # save for later phases
        self.month = month
        self.day = day
        self.img_func = img_func
        self.tts_func = tts_func

        self.logger(f"{emoji('gear')} Running event generation in background...")
        self.show_spinner()

        worker = WorkerRunnable(
            generate_and_save_events,
            month, day, event_func, output_dir, self.logger, num_events
        )
        worker.signals.finished.connect(self.on_event_generation_finished)
        self.thread_pool.start(worker)

    def on_event_generation_finished(self, result):
        self.hide_spinner()
        if not result:
            self.logger(f"{emoji('cross_mark')} Event generation failed or returned no events.")
            return

        events, event_json_path = result
        self.event_json_path = event_json_path
        self.logger(f"{emoji('check')} Event generation complete.")

        # Proceed to next page
        self.event_review_page = EventReviewPage(
            self.event_json_path,
            show_spinner=self.show_spinner,
            hide_spinner=self.hide_spinner,
            on_complete=self.on_events_reviewed
        )
        self.pages.addWidget(self.event_review_page)
        self.pages.setCurrentWidget(self.event_review_page)

    def on_events_reviewed(self):
        self.logger(f"{emoji('check')} Events reviewed. Proceeding to asset generation...")
        self.start_asset_phase()

    def start_asset_phase(self):
        self.logger(f"{emoji('gear')} Running asset generation in background...")
        self.show_spinner()
        
        # Load reviewed events from JSON
        reviewed_events = load_reviewed_events(self.event_json_path, self.logger)

        # STEP 2: Generate image/audio assets
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        worker = WorkerRunnable(
            generate_assets_threaded,
            reviewed_events,
            self.img_func,
            self.tts_func,
            temp_dir,
            self.month,
            self.day,
            self.logger
        )
        worker.signals.finished.connect(self.on_asset_generation_finished)
        self.thread_pool.start(worker)

    def on_asset_generation_finished(self, result):
        self.hide_spinner()
        if not result:
            self.logger(f"{emoji('cross_mark')} Asset generation failed or returned no assets.")
            return

        self.event_assets, self.asset_json_path = result
        self.logger(f"{emoji('check')} Asset generation complete. Assets saved to {self.asset_json_path}")

        # Proceed to image review page
        self.image_review_page = ImageReviewPage(
            self.img_func,
            self.event_json_path,
            self.asset_json_path,
            self.show_spinner,
            self.hide_spinner,
            self.logger,
            on_complete=self.on_assets_reviewed
        )
        self.pages.addWidget(self.image_review_page)
        self.pages.setCurrentWidget(self.image_review_page)

    def on_assets_reviewed(self):
        self.logger(f"{emoji('check')} Assets reviewed. Proceeding to video export...")
        self.start_video_phase()

    def start_video_phase(self):
        self.logger(f"{emoji('gear')} Building video slides in background...")
        self.show_spinner()
        
        # --- Load reviewed data
        reviewed_events = load_reviewed_events(self.event_json_path, self.logger)
        reviewed_assets = load_reviewed_assets(self.asset_json_path, self.logger)

        # --- Build video slides
        temp_dir = Path(__file__).parent / "temp"
        
        worker = WorkerRunnable(
            build_video_segments,
            self.month,
            self.day,
            reviewed_events,
            reviewed_assets,
            self.tts_func,
            temp_dir,
            self.logger
        )

        worker.signals.finished.connect(self.on_video_segments_built)
        self.thread_pool.start(worker)

    def on_video_segments_built(self, video_paths):
        if not video_paths:
            self.logger(f"{emoji('cross_mark')} Video segment building failed or returned no paths.")
            return

        self.logger(f"{emoji('check')} Video segments built successfully. Exporting final video...")

        worker = WorkerRunnable(
            export_final_output,
            video_paths,
            self.month,
            self.day,
            self.logger
        )
        worker.signals.finished.connect(self.on_video_export_finished)
        self.thread_pool.start(worker)

    def on_video_export_finished(self, final_video_path):
        self.hide_spinner()
        if not final_video_path:
            self.logger(f"{emoji('cross_mark')} Video export failed.")
            return

        cleanup(self.logger)
        QMessageBox.information(self, "Video Complete", "Your video has been successfully exported!")
        self.logger(f"{emoji('tada')} Video export complete! Final video saved to: {final_video_path}")

        reveal_video_in_file_browser(final_video_path)
        
