# DM-Logger

## Urls

* [PyPI](https://pypi.org/project/dm-logger/)
* [GitHub](https://github.com/MykhLibs/dm-logger)

## Features

- Flexible log formatting with customizable components
- Automatic error location display for ERROR and CRITICAL levels
- Log file rotation based on size
- Separate streams for DEBUG/INFO and WARNING/ERROR/CRITICAL messages
- Support for additional parameters in log messages
- Exception logging with automatic error location detection

## Installation

```bash
pip install dm-logger
```

## Usage

### Basic Usage

For simple usage, just create a logger with a name:

```python
from dm_logger import DMLogger

# Create logger with default settings
logger = DMLogger()  # default name "Main"
# or
logger = DMLogger("my_app")  # with custom name

# Logging different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Logging with additional parameters
logger.info("Processing", task_id=123, status="running")
# Output: 01-01-2025 11:22:33.555 [INFO] [Main] {task_id: 123, status: 'running'} -- Processing

# Logging exceptions
try:
    result = 1 / 0
except Exception as e:
    logger.error(e)  # Will automatically show error location
    # Output: 01-01-2025 11:22:33.555 [ERROR] [Main] (test.py:10) ZeroDivisionError: division by zero
```

Default settings:
- Console output enabled (std_logs=True)
- File logging disabled (file_logs=False)
- Logging level set to DEBUG
- Shows datetime, level, and logger name

### Logging Level Configuration

You can set the logging level either globally for all loggers or individually per logger instance:

```python
from dm_logger import DMLogger

# Set global logging level for all logger instances
DMLogger.logging_level = "INFO"  # Default is "DEBUG"

# Create logger with global level
logger1 = DMLogger("app1")  # Will use global level (INFO)

# Override level for specific logger
logger2 = DMLogger("app2", level="DEBUG")  # This logger will use DEBUG level
```

### Formatting Configuration (optional)

FormatterConfig controls which components to show in logs. You can set it either globally for all loggers or individually per logger instance:

```python
from dm_logger import DMLogger, FormatterConfig

formatter_config = FormatterConfig(
    # Default values:
    show_datetime=True,    # Show datetime (DD-MM-YYYY HH:MM:SS.mmm)
    show_level=True,       # Show level [DEBUG], [INFO], etc.
    show_name=True,        # Show logger name [my_app]
    show_location=False    # Show call location (module.function:line)
                           # Always shown for ERROR/CRITICAL!
)

logger = DMLogger(
    "my_app",
    formatter_config=formatter_config  # If not specified, default config is used
)
```

You can also set the formatter config globally for all loggers:

```python
from dm_logger import DMLogger, FormatterConfig

# Global formatter config for all logger instances
DMLogger.formatter_config = FormatterConfig(
    show_datetime=True,
    show_level=True,
    show_name=False,  # Disable logger name globally
    show_location=False
)

# Create logger with global config
logger1 = DMLogger("app1")  # Will use global config (no logger names shown)

# Override config for specific logger
logger2 = DMLogger(
    "app2",
    formatter_config=FormatterConfig(show_name=True)  # This logger will show its name
)

# Example output from logger1: "01-01-2025 11:22:33.555 [INFO] Message"
# Example output from logger2: "01-01-2025 11:22:33.555 [INFO] [app2] Message"
```

### File Logging Configuration (optional)

To enable file logging, set file_logs=True. WriteConfig controls file logger behavior:

```python
from dm_logger import DMLogger, WriteConfig

write_config = WriteConfig(
    # Default values:
    file_name="main.log",  # Log file name
    write_mode="w",        # "w" - new file at startup, "a" - append
    max_MB=5,              # Maximum file size
    max_count=10           # Number of files for rotation
)

logger = DMLogger(
    "my_app",
    file_logs=True,            # Enable file logging
    write_config=write_config  # If not specified, default config is used
)
```

Log files are stored in the `.logs` directory in the current working directory. To change directory for all log files:

```python
from dm_logger import DMLogger

# Important: set before creating any loggers
DMLogger.LOGS_DIR_PATH = "path/to/logs"  # New directory for all logs

# Now you can create loggers
logger = DMLogger("my_app")
```

### Multiple Loggers

You can create multiple loggers with different configurations:

```python
from dm_logger import DMLogger, FormatterConfig, WriteConfig

# Console only
console_logger = DMLogger(
    "console",
    level="INFO",       # Different log level
    std_logs=True,      # To console (default)
    file_logs=False     # No file (default)
)

# File only
file_logger = DMLogger(
    "file",
    std_logs=False,     # No console
    file_logs=True,     # With file
    write_config=WriteConfig(
        file_name="background.log",
        write_mode="a"  # Append to file
    )
)

# With custom formatting
debug_logger = DMLogger(
    "debug",
    formatter_config=FormatterConfig(
        show_datetime=False,  # No datetime
        show_location=True    # Always show call location
    )
)
```

## Log Format

Default format:
```
01-01-2025 11:22:33.555 [INFO] [my_app] -- message
01-01-2025 11:22:33.555 [ERROR] (main.process:45) -- error message
01-01-2025 11:22:33.555 [ERROR] (utils.calc:10) ZeroDivisionError: division by zero
```

Log components (in order of appearance):
- Datetime: `DD-MM-YYYY HH:MM:SS.mmm`
- Level: `[DEBUG]`, `[INFO]`, `[WARNING]`, `[ERROR]`, `[CRITICAL]`
- Logger name: `[my_app]`
- Call location: `(module.function:line)`
  - Always shown for ERROR/CRITICAL
  - For other levels only if show_location=True
- Additional parameters: `{param: value}`
- Message: `-- message`
   - For exceptions `-- ExceptionType: error message`
