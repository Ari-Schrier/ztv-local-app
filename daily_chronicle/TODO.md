# TODO - Daily Chronicle Generator

## ✅ Current Status

- Notebook successfully refactored into modular Python code.
- Core modules:
    - `main.py` (CLI runner)
    - `generator.py` (event generation)
    - `prompts.py` (prompt templates + types)
    - `slide_generation.py` (video slides)
    - `audio_generation.py` (audio TTS)
    - `genai_client.py` (Gemini client config)
- CLI runs end-to-end generation of video.

---

## 🚀 Next Steps

### 1️⃣ Test Full End-to-End CLI Run

- [x] Run `python daily_chronicle/main.py`
- [x] Verify:
    - [x] Event JSON saved
    - [x] 16 events are generated (not just 12)
    - [x] Images generated correctly
    - [x] Audio generated correctly
    - [x] Video written correctly
    - [x] Temporary files cleaned up

---

### 2️⃣ First Review Checkpoint: **Event JSON Editing**

**After initial event JSON is generated:**

- [x] Reject an event
- [x] Edit wording of an event or image_prompt

✅ Complete for now — see standing questions re: regeneration

---

### 3️⃣ Second Review Checkpoint: **Image Review GUI**

**After images are generated:**

- [x] Regenerate an image
- [x] Replace an image (file picker or URL)
- [x] Reject event entirely (e.g., from 16 generated, only accept best 12)
- [x] Save reduced set of events to final event JSON

---

### 4️⃣ Prompt & Content Tuning

- [ ] Update `EVENT_GENERATION_PROMPT_TEMPLATE`:
    - [x] Ensure **1 of the 12 events is a famous birthday**
    - [x] Prompt-tune to **4th grade reading level** (currently tuned to 6th grade)
    - [x] Explicitly **discourage duplicate events**
- [ ] Make birthday events visually distinct:
    - [ ] Add overlay: 🎉 confetti, 🎈 balloons, or a 🎂 banner
    - [ ] (Optional) Animated confetti with MoviePy or overlay frame

---

### 5️⃣ Speed & Optimization

- [x] Replace MoviePy `concatenate_videoclips` with optimized `ffmpeg` calls
    - [x] Research and implement `.txt`-based concat list
    - [x] Benchmark speed vs. current flow (target: <10 mins total runtime)

---

### 6️⃣ Code Quality & Readability

- [ ] Add docstrings and inline comments for all major functions
- [ ] Improve readability across all modules

---

### 7️⃣ Add OpenAI API Support (Optional/Fallback)

- [ ] Add support for OpenAI TTS via API key
- [ ] Add support for OpenAI image generation via API key
- [ ] Allow toggling Gemini vs OpenAI via config or CLI flag

---

### 8️⃣ Polish & UX Improvements

- [x] Improve video styling (typography, transitions, and pacing)
- [x] Save final reviewed `event.json` with the output `.mp4`
- [x] Image fail placeholder text needs to be notched down
- [x] Tune voice delivery:
    - [x] More **professorial**, **slower**, and in **lower vocal register**
- [x] Events should appear in **chronological order**, not generation order

---

## 🧠 Standing Questions

- Do we want the ability to **regenerate an event** at the first review checkpoint (JSON editing)?

---

## 🌱 Stretch Goals

- [ ] Build Docker container for local + cloud runs
