"""Regenera el fallback embebido de diapositivas en app.js sin pisar la lógica."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLIDES = ROOT / "docs" / "presentation" / "slides.json"
APP_JS = ROOT / "docs" / "presentation" / "app.js"

slides_data = json.loads(SLIDES.read_text(encoding="utf-8"))
fallback = json.dumps(slides_data["slides"], ensure_ascii=False, indent=2)
src = APP_JS.read_text(encoding="utf-8")
new_src, n = re.subn(
    r"const FALLBACK_SLIDES = \[[\s\S]*?\n\];",
    "const FALLBACK_SLIDES = " + fallback + ";",
    src,
    count=1,
)
if n != 1:
    raise SystemExit(f"No se pudo actualizar FALLBACK_SLIDES (coincidencias: {n})")
APP_JS.write_text(new_src, encoding="utf-8")
print("Actualizado FALLBACK_SLIDES en docs/presentation/app.js")
