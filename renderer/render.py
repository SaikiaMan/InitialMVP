"""
Render all scene/lesson JSON files in scenes/ to SVG under output/.
Validates against schema, supports rect/circle/text, and writes scenes/index.json for the frontend.
Run from project root: python renderer/render.py
"""
import json
from jsonschema import validate, ValidationError
from pathlib import Path

# Paths relative to project root
ROOT = Path(__file__).resolve().parent.parent
SCENES_DIR = ROOT / "scenes"
SCHEMA_PATH = ROOT / "schema" / "visual_scene.schema.json"
OUTPUT_DIR = ROOT / "output"
INDEX_PATH = SCENES_DIR / "index.json"


def normalize(data):
    """Convert objects-array format to schema format (scene object + timeline)."""
    if "objects" in data and "scene" not in data:
        scene_map = {}
        for obj in data["objects"]:
            o = {k: v for k, v in obj.items() if k != "id"}
            if "color" in o:
                o["fill"] = o.pop("color")
            scene_map[obj["id"]] = o
        return {"scene": scene_map, "timeline": data["timeline"]}
    return data


def ensure_lesson_has_svg(data, stem):
    """If lesson has scene+timeline but no svg, set svg to /output/{stem}.svg."""
    if "svg" not in data and "scene" in data and "timeline" in data:
        data = dict(data)
        data["svg"] = f"/output/{stem}.svg"
    return data


def render_svg(data):
    """Build SVG from validated data['scene']."""
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for obj_id, obj in data["scene"].items():
        t = obj.get("type", "rect")
        x, y = obj["x"], obj["y"]
        fill = obj.get("fill", "#2196f3")
        if t == "rect":
            w = obj.get("width", 100)
            h = obj.get("height", 50)
            lines.append(
                f'<rect id="{obj_id}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" />'
            )
        elif t == "circle":
            r = obj.get("radius", 20)
            lines.append(
                f'<circle id="{obj_id}" cx="{x}" cy="{y}" r="{r}" fill="{fill}" />'
            )
        elif t == "text":
            text = obj.get("text", "")
            lines.append(
                f'<text id="{obj_id}" x="{x}" y="{y}" fill="{fill}" font-size="16" font-family="sans-serif">{text}</text>'
            )
    lines.append("</svg>")
    return "\n".join(lines)


def main():
    schema = json.loads(SCHEMA_PATH.read_text())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    index_entries = []

    for path in sorted(SCENES_DIR.glob("*.json")):
        if path.name == "index.json":
            continue
        stem = path.stem
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"  Skip {path.name}: invalid JSON - {e}")
            continue
        data = normalize(data)
        if "scene" not in data or "timeline" not in data:
            print(f"  Skip {path.name}: no scene+timeline")
            continue
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            print(f"  Skip {path.name}: schema validation - {e.message}")
            continue
        data = ensure_lesson_has_svg(data, stem)
        svg = render_svg(data)
        out_path = OUTPUT_DIR / f"{stem}.svg"
        out_path.write_text(svg)
        print(f"  Rendered: {stem}.json -> output/{stem}.svg")

        name = (data.get("meta") or {}).get("topic", stem.replace("_", " ").title())
        index_entries.append({"name": name, "file": path.name})

    INDEX_PATH.write_text(json.dumps({"lessons": index_entries}, indent=2))
    print(f"  Index: scenes/index.json ({len(index_entries)} lessons)")
    print("Done.")


if __name__ == "__main__":
    main()
