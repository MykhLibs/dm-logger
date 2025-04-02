import logging
from dataclasses import dataclass


@dataclass
class FormatterConfig:
    show_datetime: bool = True
    show_level: bool = True
    show_name: bool = True
    show_location: bool = False


class CustomFormatter:
    date_format: str = "%d-%m-%Y %H:%M:%S"
    datetime_template: str = "%(asctime)s.%(msecs)03d"
    level_template: str = "[%(levelname)s]"
    name_template: str = "[%(name)s]"
    location_template: str = "(%(module)s.%(funcName)s:%(lineno)d)"
    message_template: str = "%(message)s"

    def __init__(self, config: FormatterConfig = None):
        self._config = config or FormatterConfig()
        self._formatter = self._create_formatter()

    @property
    def formatter(self) -> logging.Formatter:
        return self._formatter

    def _create_formatter(self) -> logging.Formatter:
        format_parts = []
        if self._config.show_datetime:
            format_parts.append(self.datetime_template)
        if self._config.show_level:
            format_parts.append(self.level_template)
        if self._config.show_name:
            format_parts.append(self.name_template)
        if self._config.show_location:
            format_parts.append(self.location_template)
        format_parts.append(self.message_template)
        format_string = " ".join(format_parts)

        return self._ErrorCriticalFormatter(
            format_string,
            datefmt=self.date_format,
            location_template=self.location_template
        )

    class _ErrorCriticalFormatter(logging.Formatter):
        def __init__(self, fmt=None, datefmt=None, style='%', validate=True, *, location_template=None):
            super().__init__(fmt, datefmt, style, validate)
            self._location_template = location_template or "(%(module)s.%(funcName)s:%(lineno)d)"

        def format(self, record):
            original_format = str(self._style._fmt)
            original_msg = record.msg

            if record.levelno >= logging.ERROR:
                # Check if we have error location info
                if hasattr(record, "error_module"):
                    error_location = f"({record.error_module}.{record.error_funcName}:{record.error_lineno})"
                    # Add location before message
                    message_idx = self._style._fmt.find("%(message)s")
                    if message_idx != -1:
                        self._style._fmt = (
                            self._style._fmt[:message_idx] +
                            error_location + " " +
                            self._style._fmt[message_idx:]
                        )
                        # If this Exception, add error type
                        if hasattr(record, "error_type"):
                            msg_parts = record.msg.split(" ")
                            record.msg = f"{msg_parts[0]} {record.error_type}: {' '.join(msg_parts[1:])}"
                # If no error location, add default location
                elif self._location_template not in self._style._fmt:
                    message_idx = self._style._fmt.find("%(message)s")
                    if message_idx != -1:
                        self._style._fmt = (
                            self._style._fmt[:message_idx] +
                            self._location_template + " " +
                            self._style._fmt[message_idx:]
                        )

            result = super().format(record)
            self._style._fmt = original_format
            record.msg = original_msg
            return result
