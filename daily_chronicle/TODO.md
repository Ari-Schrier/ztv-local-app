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

- [ ] Run `python daily_chronicle/main.py`
- [ ] Verify:
    - [ ] Event JSON saved
    - [ ] Images generated correctly
    - [ ] Audio generated correctly
    - [ ] Video written correctly
    - [ ] Temporary files cleaned up

---

### 2️⃣ First Review Checkpoint: **Event JSON Editing**

**After initial event JSON is generated:**

- [ ] Add interactive CLI (or GUI) to:
    - [ ] Reject an event
    - [ ] Regenerate an event
    - [ ] Edit wording of an event or image_prompt

**This occurs before image generation.**

---

### 3️⃣ Second Review Checkpoint: **Image Review GUI**

**After images are generated:**

- [ ] Add interactive GUI to:
    - [ ] Regenerate an image
    - [ ] Replace an image (file picker or URL)
    - [ ] Reject event entirely

---

### 4️⃣ Prompt Template Update

- [ ] Ensure that **1 of the 12 events is a famous person's birthday**.
    - [ ] Update `EVENT_GENERATION_PROMPT_TEMPLATE` to reflect this rule.

---

### 5️⃣ Speed Up MoviePy

- [ ] Implement **raw ffmpeg calls** for final video concatenation (replace MoviePy `concatenate_videoclips` where possible).
    - [ ] Research optimal `ffmpeg` concat pipeline.
    - [ ] Benchmark speed vs. current MoviePy.

---

### 6️⃣ Polish / Finalization

- [ ] Improve video styling (fonts, pacing, transitions)
- [ ] Switch from Gemini Live API → Gemini **TTS API** for faster, cheaper, more controllable voice.
- [ ] Save final event JSON alongside video output.

---

### Stretch Ideas

- [ ] Add CLI argument to choose output format
- [ ] Add CLI progress bar (e.g. tqdm)

---

## 🎉 Notes

- This project is now structured like **a real production Python app**.
- Easy to add **unit tests**, **CI/CD**, and **Docker** later if needed.
- The goal is to make the pipeline **fully auditable, editable, and reviewable by humans**.

---

