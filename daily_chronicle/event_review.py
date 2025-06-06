# event_review.py

import tkinter as tk
from tkinter import messagebox
import json
import os

class EventReviewWindow:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.events = self.load_events()
        self.current_index = 0

        self.root = tk.Tk()
        self.root.title("Daily Chronicle — Event Review")

        # Event fields
        self.text_box = tk.Text(self.root, width=80, height=20, font=("Arial", 12))
        self.text_box.pack(padx=10, pady=10)

        # Navigation buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.prev_button = tk.Button(button_frame, text="Previous", command=self.prev_event)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = tk.Button(button_frame, text="Next", command=self.next_event)
        self.next_button.grid(row=0, column=1, padx=5)

        self.reject_button = tk.Button(button_frame, text="Reject Event", command=self.reject_event, bg="red", fg="white")
        self.reject_button.grid(row=0, column=2, padx=5)

        self.save_button = tk.Button(button_frame, text="Save & Continue", command=self.save_and_exit, bg="green", fg="white")
        self.save_button.grid(row=0, column=3, padx=5)

        self.update_text_box()

    def load_events(self):
        with open(self.json_path, "r") as f:
            data = json.load(f)
        # Assuming structure: [{ "events": [...] }]
        if isinstance(data, list) and "events" in data[0]:
            return data[0]["events"]
        else:
            messagebox.showerror("Error", "Invalid JSON structure.")
            self.root.destroy()
            return []

    def update_text_box(self):
        if not self.events:
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, "No more events.")
            return

        event = self.events[self.current_index]
        display_text = json.dumps(event, indent=2)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, display_text)

        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_index < len(self.events) - 1 else tk.DISABLED)

    def prev_event(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_text_box()

    def next_event(self):
        if self.current_index < len(self.events) - 1:
            self.current_index += 1
            self.update_text_box()

    def reject_event(self):
        if not self.events:
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to reject this event?")
        if confirm:
            del self.events[self.current_index]
            if self.current_index >= len(self.events):
                self.current_index = max(0, len(self.events) - 1)
            self.update_text_box()

    def save_and_exit(self):
        # Save updated JSON
        updated_data = [{"events": self.events}]
        with open(self.json_path, "w") as f:
            json.dump(updated_data, f, indent=2)
        messagebox.showinfo("Saved", "Events saved. Proceeding to next step.")
        self.root.quit()

    def run(self):
        self.root.mainloop()

# Example usage:
if __name__ == "__main__":
    EventReviewWindow("outputs/daily_chronicle_May_30.json").run()
