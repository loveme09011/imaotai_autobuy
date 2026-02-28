from unittest.mock import MagicMock, patch, call

import pytest
import schedule


# ── jobs tests ──


class TestReservationJob:
    @patch("scheduler.jobs._save_results")
    @patch("scheduler.jobs.run_all")
    def test_calls_run_all_and_returns_results(self, mock_run_all, mock_save):
        mock_run_all.return_value = [
            {"mobile": "138", "success": True, "message": "ok"},
        ]
        from scheduler.jobs import reservation_job

        results = reservation_job("cfg.yaml", ["10056"], "520100")
        mock_run_all.assert_called_once_with("cfg.yaml", ["10056"], "520100")
        assert len(results) == 1
        assert results[0]["success"] is True

    @patch("scheduler.jobs._save_results")
    @patch("scheduler.jobs.run_all")
    def test_returns_empty_when_no_accounts(self, mock_run_all, mock_save):
        mock_run_all.return_value = []
        from scheduler.jobs import reservation_job

        results = reservation_job("cfg.yaml", ["10056"], "520100")
        assert results == []

    @patch("scheduler.jobs._save_results")
    @patch("scheduler.jobs.run_all")
    def test_saves_results(self, mock_run_all, mock_save):
        results_data = [{"mobile": "138", "success": True, "message": "ok"}]
        mock_run_all.return_value = results_data
        from scheduler.jobs import reservation_job

        reservation_job("cfg.yaml", ["10056"], "520100")
        mock_save.assert_called_once_with(results_data)

    @patch("scheduler.jobs._save_results")
    @patch("scheduler.jobs.run_all")
    def test_multi_item_codes(self, mock_run_all, mock_save):
        mock_run_all.return_value = []
        from scheduler.jobs import reservation_job

        reservation_job("cfg.yaml", ["10056", "10016"], "520100")
        mock_run_all.assert_called_once_with("cfg.yaml", ["10056", "10016"], "520100")


class TestTravelJob:
    @patch("scheduler.jobs.ApiClient")
    @patch("scheduler.jobs.load_accounts")
    def test_travel_success(self, mock_load, mock_client_cls):
        mock_load.return_value = [
            {"mobile": "13800000001", "token": "t", "device_id": "d", "user_id": "u"},
        ]
        mock_client = MagicMock()
        mock_client.travel.return_value = {"code": 2000, "message": "成功"}
        mock_client_cls.return_value = mock_client

        from scheduler.jobs import travel_job

        results = travel_job("cfg.yaml")
        assert len(results) == 1
        assert results[0]["success"] is True

    @patch("scheduler.jobs.ApiClient")
    @patch("scheduler.jobs.load_accounts")
    def test_travel_failure(self, mock_load, mock_client_cls):
        mock_load.return_value = [
            {"mobile": "13800000001", "token": "t", "device_id": "d", "user_id": "u"},
        ]
        mock_client = MagicMock()
        mock_client.travel.return_value = {"code": 4001, "message": "失败"}
        mock_client_cls.return_value = mock_client

        from scheduler.jobs import travel_job

        results = travel_job("cfg.yaml")
        assert len(results) == 1
        assert results[0]["success"] is False

    @patch("scheduler.jobs.ApiClient")
    @patch("scheduler.jobs.load_accounts")
    def test_travel_exception(self, mock_load, mock_client_cls):
        mock_load.return_value = [
            {"mobile": "13800000001", "token": "t", "device_id": "d", "user_id": "u"},
        ]
        mock_client_cls.side_effect = Exception("网络错误")

        from scheduler.jobs import travel_job

        results = travel_job("cfg.yaml")
        assert results[0]["success"] is False
        assert "网络错误" in results[0]["message"]

    @patch("scheduler.jobs.load_accounts")
    def test_travel_no_accounts(self, mock_load):
        mock_load.return_value = []

        from scheduler.jobs import travel_job

        results = travel_job("cfg.yaml")
        assert results == []


# ── runner tests ──


class TestRunner:
    def setup_method(self):
        schedule.clear()

    def teardown_method(self):
        schedule.clear()

    @patch("scheduler.runner.travel_job")
    @patch("scheduler.runner.reservation_job")
    def test_setup_registers_jobs(self, mock_res_job, mock_travel_job):
        from scheduler.runner import setup

        setup("cfg.yaml", ["10056"], "520100")

        jobs = schedule.get_jobs()
        assert len(jobs) == 2

        tags = {tag for job in jobs for tag in job.tags}
        assert "reservation" in tags
        assert "travel" in tags

    @patch("scheduler.runner.travel_job")
    @patch("scheduler.runner.reservation_job")
    def test_reservation_job_at_0900(self, mock_res_job, mock_travel_job):
        from scheduler.runner import setup

        setup("cfg.yaml", ["10056"], "520100")

        res_jobs = [j for j in schedule.get_jobs() if "reservation" in j.tags]
        assert len(res_jobs) == 1
        assert res_jobs[0].at_time.strftime("%H:%M:%S") == "09:00:00"

    @patch("scheduler.runner.travel_job")
    @patch("scheduler.runner.reservation_job")
    def test_travel_job_in_range(self, mock_res_job, mock_travel_job):
        from scheduler.runner import setup

        setup("cfg.yaml", ["10056"], "520100")

        travel_jobs = [j for j in schedule.get_jobs() if "travel" in j.tags]
        assert len(travel_jobs) == 1
        hour = travel_jobs[0].at_time.hour
        assert 10 <= hour <= 19

    def test_random_travel_time_format(self):
        from scheduler.runner import _random_travel_time

        for _ in range(20):
            t = _random_travel_time()
            parts = t.split(":")
            assert len(parts) == 3
            h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
            assert 10 <= h <= 19
            assert 0 <= m <= 59
            assert 0 <= s <= 59
