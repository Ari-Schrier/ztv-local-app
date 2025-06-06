# event_review.py

import json
import dearpygui.dearpygui as dpg

# Global editing flag
is_editing = False

# Load/save events
def load_events(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    if isinstance(data, list) and all(isinstance(event, dict) for event in data):
        return data
    else:
        raise ValueError("Invalid JSON structure — expected flat list of event dicts.")

def save_events(json_path, events):
    with open(json_path, "w") as f:
        json.dump(events, f, indent=2)

# Update display
def update_event_display(events, index):
    if not events:
        dpg.set_value("event_counter", "Event 0 of 0")
        dpg.set_value("preview_text", "")
        dpg.set_value("event_textbox", "")
        return

    event = events[index]
    dpg.set_value("event_counter", f"Event {index + 1} of {len(events)}")

    display_text = json.dumps(event, indent=2)

    # Update BOTH preview and editor
    dpg.set_value("preview_text", display_text)
    dpg.set_value("event_textbox", display_text)

    # Enable/disable nav
    dpg.configure_item("prev_button", enabled=(index > 0))
    dpg.configure_item("next_button", enabled=(index < len(events) - 1))

# Save current event
def save_current_event(events, index):
    try:
        raw_text = dpg.get_value("event_textbox")
        parsed_event = json.loads(raw_text)
        events[index] = parsed_event
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON — not saving current event.")

# Toggle Edit mode
def toggle_edit_mode(sender, app_data, user_data):
    global is_editing
    is_editing = not is_editing

    dpg.configure_item("preview_text", show=not is_editing)
    dpg.configure_item("json_editor_child", show=is_editing)
    dpg.configure_item("edit_button", label="Done Editing" if is_editing else "Edit")

    # If exiting edit mode, save current editor to preview
    if not is_editing:
        try:
            raw_text = dpg.get_value("event_textbox")
            parsed_event = json.loads(raw_text)
            pretty_text = json.dumps(parsed_event, indent=2)
            dpg.set_value("preview_text", pretty_text)
        except json.JSONDecodeError:
            print("⚠️ Invalid JSON — preview not updated.")

# Navigation callbacks
def on_prev(sender, app_data, user_data):
    save_current_event(user_data["events"], user_data["index"])
    user_data["index"] -= 1
    update_event_display(user_data["events"], user_data["index"])

def on_next(sender, app_data, user_data):
    save_current_event(user_data["events"], user_data["index"])
    user_data["index"] += 1
    update_event_display(user_data["events"], user_data["index"])

def on_reject(sender, app_data, user_data):
    if not user_data["events"]:
        return
    save_current_event(user_data["events"], user_data["index"])
    current_index = user_data["index"]
    del user_data["events"][current_index]
    if current_index >= len(user_data["events"]):
        user_data["index"] = max(0, len(user_data["events"]) - 1)
    update_event_display(user_data["events"], user_data["index"])

def on_save_and_exit(sender, app_data, user_data):
    save_current_event(user_data["events"], user_data["index"])
    save_events(user_data["json_path"], user_data["events"])
    print("✅ Events saved. Exiting.")
    dpg.stop_dearpygui()

# Main launcher
def launch_event_review_window(json_path):
    dpg.create_context()

    # Load data
    events = load_events(json_path)
    user_data = {
        "json_path": json_path,
        "events": events,
        "index": 0
    }

    with dpg.window(label="Daily Chronicle — Event Review", width=1200, height=800):

        dpg.add_text("", tag="event_counter")
        dpg.add_separator()

        # Preview Mode (word wrapped)
        dpg.add_input_text(
            tag="preview_text",
            multiline=True,
            readonly=True,
            width=-1,
            height=500,
            no_horizontal_scroll=True
        )

        # Edit Mode (scrollable JSON), hidden initially
        with dpg.child_window(tag="json_editor_child", width=-1, height=500, horizontal_scrollbar=True, show=False):
            dpg.add_input_text(
                tag="event_textbox",
                multiline=True,
                width=3000,
                height=500,
                tab_input=True
            )

        dpg.add_button(label="Edit", tag="edit_button", callback=toggle_edit_mode)

        dpg.add_separator()

        # Navigation buttons
        with dpg.group(horizontal=True):
            dpg.add_button(label="Previous", tag="prev_button", callback=on_prev, user_data=user_data)
            dpg.add_button(label="Next", tag="next_button", callback=on_next, user_data=user_data)
            dpg.add_button(label="Reject Event", callback=on_reject, user_data=user_data)
            dpg.add_button(label="Save & Continue", callback=on_save_and_exit, user_data=user_data)

    # Init viewport
    dpg.create_viewport(title="Daily Chronicle - Event Review", width=1200, height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Initial display
    update_event_display(events, 0)

    dpg.start_dearpygui()
    dpg.destroy_context()

# Example usage
if __name__ == "__main__":
    launch_event_review_window("outputs/daily_chronicle_June_6.json")
