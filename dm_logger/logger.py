from __future__ import annotations
import re
import sys
import os
import logging
from typing import Literal
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler

from .formatter import CustomFormatter, FormatterConfig
from .filters import DebugInfoFilter, WarningErrorCriticalFilter


@dataclass
class WriteConfig:
    file_name: str = "main.log"
    write_mode: Literal["a", "w"] = "w"
    max_MB: int = 5
    max_count: int = 10


class DMLogger:
    LOGS_DIR_PATH: str = ".logs"
    formatter_config: FormatterConfig = FormatterConfig()
    _loggers: dict = {}
    _file_handlers: dict = {}

    def __new__(cls, name: str = "Main", *args, **kwargs):
        if name not in cls._loggers:
            cls._loggers[name] = super().__new__(cls)
        return cls._loggers[name]

    def __init__(
        self,
        name: str = "Main",
        level: str = "DEBUG",
        *,
        std_logs: bool = True,
        file_logs: bool = False,
        write_config: WriteConfig = None,
        formatter_config: FormatterConfig = None,
    ):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self._name = name
        self._logger = logging.getLogger(name)
        level = logging.getLevelName(level.upper())
        self._logger.setLevel(level)

        formatter_config = formatter_config or self.formatter_config
        formatter = CustomFormatter(formatter_config).formatter
        if std_logs:
            self._set_std_handlers(formatter)
        if file_logs:
            write_config = write_config or WriteConfig()
            self._set_rotating_file_handler(write_config, formatter)

    def debug(self, message: any = None, **kwargs) -> None:
        self._log(self._logger.debug, message, **kwargs)

    def info(self, message: any = None, **kwargs) -> None:
        self._log(self._logger.info, message, **kwargs)

    def warning(self, message: any = None, **kwargs) -> None:
        self._log(self._logger.warning, message, **kwargs)

    def error(self, message: any = None, **kwargs) -> None:
        self._log(self._logger.error, message, **kwargs)

    def critical(self, message: any = None, **kwargs) -> None:
        self._log(self._logger.critical, message, **kwargs)

    @staticmethod
    def _log(level_func: callable, message: any, **kwargs) -> None:
        if not logging.getLogger().handlers and not level_func.__self__.handlers:
            return

        extra = {}

        if isinstance(message, Exception):
            # If an exception was thrown, we find the last frame from its stack
            tb = message.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            extra = {
                "error_module": tb.tb_frame.f_code.co_filename.split('\\')[-1].replace(".py", ""),
                "error_funcName": tb.tb_frame.f_code.co_name,
                "error_lineno": tb.tb_lineno,
                "error_type": message.__class__.__name__
            }
            message = str(message)

        message = "-- " + str(message) if message else ""
        if kwargs:
            dict_string = re.sub(r"'(\w+)':", r"\1:", str(kwargs))
            message = f"{dict_string} {message}"

        level_func(message, stacklevel=3, extra=extra)

    def _set_std_handlers(self, formatter: logging.Formatter) -> None:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.addFilter(DebugInfoFilter())
        stdout_handler.setFormatter(formatter)
        self._logger.addHandler(stdout_handler)

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.addFilter(WarningErrorCriticalFilter())
        stderr_handler.setFormatter(formatter)
        self._logger.addHandler(stderr_handler)

    def _set_rotating_file_handler(self, write_config: WriteConfig, formatter: logging.Formatter) -> None:
        file_name = write_config.file_name or self._name
        if file_name not in self._file_handlers:
            self._file_handlers[file_name] = self._get_rotating_file_handler(file_name, write_config, formatter)
        self._logger.addHandler(self._file_handlers[file_name])

    @classmethod
    def _get_rotating_file_handler(
        cls,
        file_name: str,
        write_config: WriteConfig,
        formatter: logging.Formatter
    ) -> RotatingFileHandler:
        logs_dir_path = os.path.normpath(cls.LOGS_DIR_PATH or ".logs")
        if not os.path.exists(logs_dir_path):
            os.makedirs(logs_dir_path)
        log_path = os.path.join(logs_dir_path, file_name)
        max_bytes = write_config.max_MB * 1024 * 1024

        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=max_bytes,
            backupCount=write_config.max_count,
            encoding="utf-8"
        )
        if write_config.write_mode == "w" and os.path.exists(log_path) and os.path.getsize(log_path) > 0:
            file_handler.doRollover()
        file_handler.setFormatter(formatter)
        return file_handler
