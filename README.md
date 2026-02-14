# JSON Schema Visual Lessons

Run everything locally:

1. **Build all scenes and start the server**
   ```bash
   python run.py
   ```
2. **Open in browser:** http://localhost:8000/frontend/

Or step by step:

- **Build only** (validate scenes, render SVGs, create lesson index):
  ```bash
  python renderer/render.py
  ```
- **Serve only** (must have run the renderer first):
  ```bash
  python -m http.server 8000
  ```
  Then open http://localhost:8000/frontend/

## Layout

- **scenes/** – Lesson JSON files (schema: `scene` + `timeline`, optional `svg`, `meta`). Each is validated and rendered to **output/*.svg**. `scenes/index.json` is generated for the frontend.
- **schema/** – `visual_scene.schema.json` defines scene objects (rect, circle, text) and timeline steps (show, hide, move, highlight).
- **output/** – Generated SVGs (do not edit by hand).
- **frontend/** – Single-page app: lesson selector, Play/Reset, timeline animation.
- **renderer/render.py** – Reads all `scenes/*.json`, normalizes `objects`→`scene` and `color`→`fill`, validates, and writes `output/{name}.svg` plus `scenes/index.json`.

## Adding a lesson

Add a new `scenes/your_lesson.json` with `scene`, `timeline`, and optional `meta.topic`. Run `python renderer/render.py` (or `python run.py`). It will appear in the dropdown and use `output/your_lesson.svg`.
