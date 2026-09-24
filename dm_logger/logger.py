from __future__ import annotations
import re
import sys
import os
import logging
import copy
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
    level: str | int | None = None


class DMLogger:
    LOGS_DIR_PATH: str = ".logs"
    logging_level: str = "DEBUG"
    std_logging_level: str | int | None = None
    write_config: WriteConfig = WriteConfig()
    formatter_config: FormatterConfig = FormatterConfig()
    _loggers: dict = {}
    _file_handlers: dict = {}

    def __new__(cls, name: str = "Main", *args, **kwargs):
        if name not in cls._loggers:
            cls._loggers[name] = super().__new__(cls)
        return cls._loggers[name]

    @classmethod
    def _resolve_level(cls, level: str | int | None) -> int:
        if level is None:
            return logging.DEBUG
        if isinstance(level, int):
            return level
        resolved = logging.getLevelName(str(level).upper())
        if isinstance(resolved, int):
            return resolved
        return logging.DEBUG

    def __init__(
        self,
        name: str = "Main",
        level: str | int = None,
        *,
        std_logs: bool = True,
        file_logs: bool = False,
        std_level: str | int = None,
        file_level: str | int = None,
        write_config: WriteConfig = None,
        formatter_config: FormatterConfig = None,
    ):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self._name = name
        self._logger = logging.getLogger(name)

        # 1. Resolve WriteConfig (single source of truth for file logging)
        wc = copy.copy(write_config or self.write_config)
        if file_level is not None:
            wc.level = file_level
        elif wc.level is None:
            wc.level = level or self.logging_level

        file_lvl = self._resolve_level(wc.level)

        # 2. Resolve std level (for console)
        std_lvl = self._resolve_level(
            std_level or self.std_logging_level or level or self.logging_level
        )

        # 3. Calculate root logger level
        active_levels = []
        if std_logs:
            active_levels.append(std_lvl)
        if file_logs:
            active_levels.append(file_lvl)
        if not active_levels:
            active_levels.append(self._resolve_level(level or self.logging_level))

        self._logger.setLevel(min(active_levels))

        # 4. Attach handlers
        formatter_config = formatter_config or self.formatter_config
        formatter = CustomFormatter(formatter_config).formatter
        if std_logs:
            self._set_std_handlers(formatter, std_level=std_lvl)
        if file_logs:
            self._set_rotating_file_handler(wc, formatter, file_level=file_lvl)

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
            kwargs = re.sub(r"'(\w+)':", r"\1:", str(kwargs))
            message = f"{kwargs}$kwargs${message}"

        level_func(message, stacklevel=3, extra=extra)

    def _set_std_handlers(self, formatter: logging.Formatter, std_level: int = logging.DEBUG) -> None:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(std_level)
        stdout_handler.addFilter(DebugInfoFilter())
        stdout_handler.setFormatter(formatter)
        self._logger.addHandler(stdout_handler)

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_level = max(std_level, logging.WARNING)
        stderr_handler.setLevel(stderr_level)
        stderr_handler.addFilter(WarningErrorCriticalFilter())
        stderr_handler.setFormatter(formatter)
        self._logger.addHandler(stderr_handler)

    def _set_rotating_file_handler(
        self,
        write_config: WriteConfig,
        formatter: logging.Formatter,
        file_level: int = logging.DEBUG,
    ) -> None:
        file_name = write_config.file_name or self._name
        if file_name not in self._file_handlers:
            self._file_handlers[file_name] = self._get_rotating_file_handler(
                file_name, write_config, formatter, file_level=file_level
            )
        else:
            if file_level < self._file_handlers[file_name].level:
                self._file_handlers[file_name].setLevel(file_level)
        self._logger.addHandler(self._file_handlers[file_name])

    @classmethod
    def _get_rotating_file_handler(
        cls,
        file_name: str,
        write_config: WriteConfig,
        formatter: logging.Formatter,
        file_level: int = logging.DEBUG,
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
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        return file_handler
