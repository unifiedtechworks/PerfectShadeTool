"""Tests for local proposal output path helpers."""

from pathlib import Path

from app.storage import sanitize_filename_part, unique_path


def test_sanitize_filename_part_removes_windows_unsafe_characters() -> None:
    assert sanitize_filename_part('  ACME: West / Phase*1?  ') == "ACME West Phase1"
    assert sanitize_filename_part("Project... ") == "Project"


def test_sanitize_filename_part_uses_fallback_for_empty_result() -> None:
    assert sanitize_filename_part('  <>:"/\\|?*  ') == "Untitled Project"


def test_unique_path_adds_incrementing_suffix(tmp_path: Path) -> None:
    requested = tmp_path / "proposal.json"
    requested.touch()
    (tmp_path / "proposal (2).json").touch()

    assert unique_path(requested) == tmp_path / "proposal (3).json"


def test_unique_path_returns_unused_path_unchanged(tmp_path: Path) -> None:
    requested = tmp_path / "proposal.docx"
    assert unique_path(requested) == requested
