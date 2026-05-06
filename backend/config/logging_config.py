"""Lightweight logging helpers for the backend."""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"
    LABELS = {
        "DEBUG": "DBG",
        "INFO": "INF",
        "WARNING": "WRN",
        "ERROR": "ERR",
        "CRITICAL": "CRT",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        label = self.LABELS.get(record.levelname, record.levelname)
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        if record.levelno >= logging.ERROR:
            message = f"{label} {timestamp} | {record.filename}:{record.lineno} | {record.funcName}() | {record.getMessage()}"
        elif record.levelno >= logging.WARNING:
            message = f"{label} {timestamp} | {record.filename}:{record.lineno} | {record.getMessage()}"
        else:
            message = f"{label} {timestamp} | {record.getMessage()}"

        return f"{color}{message}{self.RESET}"


class SimpleLogger:
    _instances: dict[str, "SimpleLogger"] = {}

    def __new__(cls, name: str = "app", level: str = "INFO"):
        key = f"{name}_{level.upper()}"
        if key not in cls._instances:
            cls._instances[key] = super().__new__(cls)
            cls._instances[key]._initialized = False
        return cls._instances[key]

    def __init__(self, name: str = "app", level: str = "INFO"):
        if getattr(self, "_initialized", False):
            return

        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.logger.handlers.clear()

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        handler.setFormatter(ColoredFormatter())

        self.logger.addHandler(handler)
        self.logger.propagate = False
        self._initialized = True

    def debug(self, message: str, *args):
        self.logger.debug(message, *args)

    def info(self, message: str, *args):
        self.logger.info(message, *args)

    def warning(self, message: str, *args):
        self.logger.warning(message, *args)

    def error(self, message: str, *args):
        self.logger.error(message, *args)

    def critical(self, message: str, *args):
        self.logger.critical(message, *args)

    def log_api_request(self, method: str, path: str, status_code: Optional[int] = None, duration: Optional[float] = None):
        if status_code is not None and duration is not None:
            self.info("API %s %s -> %s (%.2fs)", method, path, status_code, duration)
        else:
            self.info("API %s %s", method, path)

    def log_operation_start(self, operation: str):
        self.info("Start: %s", operation)

    def log_operation_success(self, operation: str, duration: Optional[float] = None):
        if duration is not None:
            self.info("Done: %s (%.2fs)", operation, duration)
        else:
            self.info("Done: %s", operation)

    def log_operation_error(self, operation: str, error: Exception):
        self.error("Failed: %s - %s", operation, error)

    def log_data_count(self, data_type: str, count: int):
        self.info("%s: %s", data_type, count)

    def log_progress(self, current: int, total: int, operation: str = ""):
        percentage = (current / total * 100) if total > 0 else 0
        prefix = f"{operation} " if operation else ""
        self.info("%sprogress: %s/%s (%.1f%%)", prefix, current, total, percentage)


def get_logger(name: str = "app", level: str = "INFO") -> SimpleLogger:
    return SimpleLogger(name, level)


def log_function_call(logger: Optional[SimpleLogger] = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            active_logger = logger or get_logger(func.__module__)
            active_logger.debug("Calling %s", func.__name__)
            try:
                result = func(*args, **kwargs)
                active_logger.debug("%s completed", func.__name__)
                return result
            except Exception as exc:
                active_logger.error("%s failed: %s", func.__name__, exc)
                raise

        return wrapper

    return decorator


def log_execution_time(logger: Optional[SimpleLogger] = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time

            active_logger = logger or get_logger(func.__module__)
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                active_logger.info("%s completed in %.2fs", func.__name__, time.time() - start_time)
                return result
            except Exception as exc:
                active_logger.error("%s failed in %.2fs: %s", func.__name__, time.time() - start_time, exc)
                raise

        return wrapper

    return decorator
