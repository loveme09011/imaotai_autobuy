import sys

from loguru import logger

from utils.logger import setup_logger, get_logger, LOG_FORMAT


class TestSetupLogger:
    def test_setup_creates_log_dir(self, tmp_path, monkeypatch):
        import utils.logger as logger_mod

        log_dir = tmp_path / "logs"
        monkeypatch.setattr(logger_mod, "LOG_DIR", log_dir)

        logger.remove()
        setup_logger()

        assert log_dir.exists()

    def test_setup_adds_handlers(self, tmp_path, monkeypatch):
        import utils.logger as logger_mod

        monkeypatch.setattr(logger_mod, "LOG_DIR", tmp_path / "logs")

        logger.remove()
        setup_logger()

        assert len(logger._core.handlers) >= 2


class TestGetLogger:
    def test_returns_bound_logger(self):
        log = get_logger("test_module")
        assert log is not None

    def test_log_output_contains_name(self, tmp_path, monkeypatch, capsys):
        import utils.logger as logger_mod

        monkeypatch.setattr(logger_mod, "LOG_DIR", tmp_path / "logs")

        logger.remove()
        setup_logger()

        log = get_logger("my_module")
        log.info("hello")

        captured = capsys.readouterr()
        assert "my_module" in captured.err
        assert "hello" in captured.err
