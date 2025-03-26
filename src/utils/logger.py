import logging
import os
import re
from logging.handlers import RotatingFileHandler

class Logger:
    LOG_DIR = os.path.join(os.path.dirname(__file__), "../../logs")

    def __init__(self, module_name: str):
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)

        log_file = os.path.join(self.LOG_DIR, f"{module_name}.log")

        self._logger = logging.getLogger(module_name)
        self._logger.setLevel(logging.INFO)

        if not self._logger.hasHandlers():
            file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s"))

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    def sanitize(self, msg):
        return re.sub(r'[^\x00-\x7F]+', '', str(msg))

    # Overriding log methods to sanitize messages
    def info(self, msg, *args, **kwargs):
        self._logger.info(self.sanitize(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(self.sanitize(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(self.sanitize(msg), *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._logger.exception(self.sanitize(msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(self.sanitize(msg), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(self.sanitize(msg), *args, **kwargs)
