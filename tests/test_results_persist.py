import json
from pathlib import Path
from unittest.mock import patch

import pytest


class TestSaveResults:
    @pytest.fixture(autouse=True)
    def setup_tmp_dir(self, tmp_path):
        self.results_dir = tmp_path / "data" / "results"
        with patch("scheduler.jobs.RESULTS_DIR", self.results_dir):
            yield

    def test_creates_file_on_first_save(self):
        from scheduler.jobs import _save_results

        results = [{"mobile": "138", "success": True, "message": "ok"}]
        with patch("scheduler.jobs.RESULTS_DIR", self.results_dir):
            _save_results(results)

        files = list(self.results_dir.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["results"] == results

    def test_appends_to_existing_file(self):
        from scheduler.jobs import _save_results

        with patch("scheduler.jobs.RESULTS_DIR", self.results_dir):
            _save_results([{"mobile": "138", "success": True, "message": "first"}])
            _save_results([{"mobile": "139", "success": False, "message": "second"}])

        files = list(self.results_dir.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert len(data) == 2

    def test_handles_corrupted_existing_file(self):
        from scheduler.jobs import _save_results

        self.results_dir.mkdir(parents=True, exist_ok=True)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = self.results_dir / f"{today}.json"
        filepath.write_text("not valid json", encoding="utf-8")

        with patch("scheduler.jobs.RESULTS_DIR", self.results_dir):
            _save_results([{"mobile": "138", "success": True, "message": "ok"}])

        data = json.loads(filepath.read_text(encoding="utf-8"))
        assert len(data) == 1

    def test_entry_has_timestamp(self):
        from scheduler.jobs import _save_results

        with patch("scheduler.jobs.RESULTS_DIR", self.results_dir):
            _save_results([{"mobile": "138", "success": True, "message": "ok"}])

        files = list(self.results_dir.glob("*.json"))
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert "timestamp" in data[0]
