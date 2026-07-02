"""Local JSON export helpers."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re

from app.models import BidData


INVALID_FILENAME_CHARS = r'<>:"/\\|?*'


def sanitize_filename_part(value: str, fallback: str = "Untitled Project") -> str:
    """Return a Windows-safe filename component."""
    cleaned = re.sub(f"[{re.escape(INVALID_FILENAME_CHARS)}]", "", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.rstrip(". ")
    return cleaned or fallback


def unique_path(path: Path) -> Path:
    """Append (2), (3), etc. if a file already exists."""
    if not path.exists():
        return path

    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def build_json_output_path(output_folder: str, project_name: str) -> Path:
    folder = Path(output_folder).expanduser()
    safe_project_name = sanitize_filename_part(project_name)
    filename = f"{date.today().isoformat()} - {safe_project_name} - Perfect Shade Bid.json"
    return unique_path(folder / filename)


def save_bid_json(bid_data: BidData) -> Path:
    """Save bid data as JSON and return the written file path."""
    output_folder = Path(bid_data.output_folder).expanduser()
    output_folder.mkdir(parents=True, exist_ok=True)

    output_path = build_json_output_path(str(output_folder), bid_data.project_name)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(bid_data.to_dict(), file, indent=2)
    return output_path
