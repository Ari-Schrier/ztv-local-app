# daily_chronicle/image_review.py

import sys
import json
import traceback
import requests
import os

from PySide6.QtCore import (
    QObject, QRunnable, QThreadPool, Signal, Slot
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QMessageBox, QFileDialog, QFormLayout, QInputDialog
)
from PySide6.QtGui import QPixmap

from .img_utils import crop_center
from io import BytesIO
from PIL import Image

# --- Worker classes ---

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

# --- ImageReviewWindow ---

class ImageReviewWindow(QWidget):
    def __init__(self, json_path, image_paths):
        super().__init__()

        self.json_path = json_path
        self.image_paths = image_paths
        self.events = self.load_events()
        self.index = 0

        self.threadpool = QThreadPool()
        print(f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads")

        self.init_ui()
        self.update_display()

    def load_events(self):
        with open(self.json_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list) and all(isinstance(event, dict) for event in data):
            return data
        else:
            raise ValueError("Invalid JSON structure — expected flat list of event dicts.")

    def save_events(self):
        with open(self.json_path, "w") as f:
            json.dump(self.events, f, indent=2)

    def init_ui(self):
        self.setWindowTitle("Daily Chronicle — Image Review")
        self.setFixedSize(1000, 900)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Instructions
        instructions = QLabel(
            "Instructions:\n"
            "- Review each image.\n"
            "- You may edit the Image Prompt and regenerate.\n"
            "- 'Replace' lets you choose a local file or enter an image URL.\n"
            "- 'Previous' and 'Next' navigate images.\n"
            "- 'Reject Image' removes an image.\n"
            "- 'Save and Close' saves the JSON and closes this window.\n"
        )
        instructions.setWordWrap(True)
        instructions.setFixedWidth(750)
        instructions.setMaximumHeight(130)
        main_layout.addWidget(instructions)

        # Counter label
        self.counter_label = QLabel("")
        main_layout.addWidget(self.counter_label)

        # Image preview — CENTERED
        self.image_label = QLabel("Image Preview")
        self.image_label.setFixedSize(512, 512)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setScaledContents(True)

        image_layout = QHBoxLayout()
        image_layout.addStretch()
        image_layout.addWidget(self.image_label)
        image_layout.addStretch()

        main_layout.addLayout(image_layout)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)

        self.image_prompt_input = QTextEdit()
        self.image_prompt_input.setMinimumWidth(600)
        self.image_prompt_input.setFixedHeight(75)
        form_layout.addRow("Image Prompt:", self.image_prompt_input)

        main_layout.addLayout(form_layout)

        # Action buttons
        action_layout = QHBoxLayout()

        self.regen_button = QPushButton("Regenerate Image")
        self.regen_button.clicked.connect(self.on_regenerate)
        action_layout.addWidget(self.regen_button)

        self.replace_button = QPushButton("Replace Image")
        self.replace_button.clicked.connect(self.on_replace)
        action_layout.addWidget(self.replace_button)

        main_layout.addLayout(action_layout)

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.on_prev)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.on_next)
        nav_layout.addWidget(self.next_button)

        self.reject_button = QPushButton("Reject Image")
        self.reject_button.clicked.connect(self.on_reject)
        nav_layout.addWidget(self.reject_button)

        self.save_exit_button = QPushButton("Save and Close")
        self.save_exit_button.clicked.connect(self.on_save_and_exit)
        nav_layout.addWidget(self.save_exit_button)

        main_layout.addLayout(nav_layout)

        self.setLayout(main_layout)

    def update_display(self):
        if not self.image_paths:
            self.counter_label.setText("Image 0 of 0")
            self.clear_fields()
            return

        event = self.events[self.index]
        image_path = self.image_paths[self.index]

        self.counter_label.setText(f"Image {self.index + 1} of {len(self.image_paths)}")

        # Load image
        if image_path.startswith("http"):
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(image_path).content)
        elif os.path.exists(image_path):
            pixmap = QPixmap(image_path)
        else:
            pixmap = QPixmap()

        self.image_label.setPixmap(pixmap)

        # Load image prompt
        self.image_prompt_input.setPlainText(event.get("image_prompt", ""))

        # Enable/disable nav buttons
        self.prev_button.setEnabled(self.index > 0)
        self.next_button.setEnabled(self.index < len(self.image_paths) - 1)

    def save_current_event(self):
        event = self.events[self.index]
        event["image_prompt"] = self.image_prompt_input.toPlainText()

    def clear_fields(self):
        self.image_label.clear()
        self.image_prompt_input.clear()

    def on_prev(self):
        self.save_current_event()
        self.index -= 1
        self.update_display()

    def on_next(self):
        self.save_current_event()
        self.index += 1
        self.update_display()

    def on_reject(self):
        if not self.image_paths:
            return
        self.save_current_event()
        confirm = QMessageBox.question(
            self, "Confirm Reject", "Are you sure you want to reject this image?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            del self.events[self.index]
            del self.image_paths[self.index]
            if self.index >= len(self.image_paths):
                self.index = max(0, len(self.image_paths) - 1)
            self.update_display()

    def on_save_and_exit(self):
        self.save_current_event()
        self.save_events()
        QMessageBox.information(self, "Saved", "✅ Events saved.")
        self.close()

    # --- Threaded actions ---

    def on_regenerate(self):
        self.save_current_event()
        prompt_text = self.image_prompt_input.toPlainText()
        worker = Worker(self.regenerate_image, prompt_text)
        worker.signals.result.connect(self.on_regen_result)
        worker.signals.finished.connect(self.on_regen_finished)
        self.threadpool.start(worker)

    def regenerate_image(self, prompt_text):
        from daily_chronicle.genai_client import client, IMAGE_MODEL_ID
        from io import BytesIO
        from PIL import Image

        print(f"Regenerating image for prompt: {prompt_text}")

        result = client.models.generate_images(
            model=IMAGE_MODEL_ID,
            prompt=prompt_text,
            config={
                "number_of_images": 1,
                "output_mime_type": "image/jpeg",
                "aspect_ratio": "1:1",
                "safety_filter_level": "BLOCK_ONLY_HIGH",
                "person_generation": "ALLOW_ADULT"
            }
        )

        try:
            if not result.generated_images:
                raise ValueError("No images were generated.")

            image = Image.open(BytesIO(result.generated_images[0].image.image_bytes))

            save_dir = "temp/temp_image_files"
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"regen_image_{self.index + 1}.jpg")
            image.save(save_path, format="JPEG")

            return save_path

        except Exception as e:
            print("❌ Image generation failed:", e)
            return None

    def on_regen_result(self, image_path):
        if image_path:
            print(f"New image: {image_path}")
            self.image_paths[self.index] = image_path
            self.update_display()
            QMessageBox.information(self, "Regenerate Complete", "New image generated.")
        else:
            QMessageBox.warning(self, "Regenerate Failed", "Image generation failed. Please try again.")

    def on_regen_finished(self):
        print("Regeneration complete.")

    def on_replace(self):
        choice = QMessageBox.question(
            self, "Replace Image",
            "Do you want to load from URL? (Choose No for Local File)",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        if choice == QMessageBox.Cancel:
            return

        if choice == QMessageBox.Yes:
            url, ok = QInputDialog.getText(self, "Enter Image URL", "Image URL:")
            if not ok or not url.strip():
                return
            url = url.strip()

            worker = Worker(self.download_image_from_url, url)
            worker.signals.result.connect(self.on_replace_result)
            self.threadpool.start(worker)
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            if file_path:
                img = Image.open(file_path).convert("RGB")
                img = crop_center(img)

                save_dir = "temp/temp_image_files"
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"manual_image_{self.index + 1}.jpg")
                img.save(save_path, format="JPEG")

                self.image_paths[self.index] = save_path
                self.update_display()

    def download_image_from_url(self, url):
        print(f"Downloading image from: {url}")
        response = requests.get(url)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content)).convert("RGB")
        img = crop_center(img)

        save_dir = "temp/temp_image_files"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"manual_image_{self.index + 1}.jpg")
        img.save(save_path, format="JPEG")

        return save_path

    def on_replace_result(self, image_path):
        print(f"Replaced with: {image_path}")
        self.image_paths[self.index] = image_path
        self.update_display()

# --- Main launcher for standalone testing ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("temp/daily_chronicle_images_June_6.json", "r") as f:
        image_paths = json.load(f)
    window = ImageReviewWindow("outputs/daily_chronicle_June_6.json", image_paths)
    window.show()
    sys.exit(app.exec())
