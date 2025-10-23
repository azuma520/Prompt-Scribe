import sys
from pathlib import Path

NEW_SLUG = "google/gemini-2.5-flash-lite-preview-09-2025"

candidates = [
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent / ".env",
]

for env_path in candidates:
    try:
        lines = []
        found = False
        if env_path.exists():
            with env_path.open("r", encoding="utf-8-sig") as f:
                for line in f:
                    if line.lstrip("\ufeff").startswith("DEEPSEEK_MODEL="):
                        lines.append(f"DEEPSEEK_MODEL={NEW_SLUG}\n")
                        found = True
                    else:
                        lines.append(line)
        if not found:
            lines.append(f"DEEPSEEK_MODEL={NEW_SLUG}\n")
        with env_path.open("w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"Updated: {env_path}")
    except Exception as e:
        print(f"Failed to update {env_path}: {e}")
