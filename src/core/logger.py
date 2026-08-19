import os
import datetime

class Logger:
    def __init__(self, log_dir=None):
        if log_dir is None:
            log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
        self.log_dir = os.path.abspath(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"configurador_{timestamp_str}.log")

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"

        # Write silently to file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception:
            pass

    def log_raw(self, raw_text: str):
        """Writes raw subprocess output directly into the log file."""
        if not raw_text:
            return
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(raw_text.rstrip() + "\n")
        except Exception:
            pass

_logger_instance = None

def get_logger(log_dir=None):
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger(log_dir)
    return _logger_instance
