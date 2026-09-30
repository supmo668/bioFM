"""T3: exactly one Modal producer writes lifecycle_runs.jsonl (the trainer's own process)."""
from pathlib import Path

MODAL_DIR = Path(__file__).parents[1] / "scripts" / "modal"


def test_lifecycle_only_app_is_deleted():
    assert not (MODAL_DIR / "app_v05_lifecycle_only.py").exists()


def test_exactly_one_modal_file_writes_lifecycle_runs():
    producers = [
        p.name for p in sorted(MODAL_DIR.glob("*.py"))
        if "lifecycle_runs.jsonl" in p.read_text(encoding="utf-8")
    ]
    assert producers == ["app_v05.py"], producers
