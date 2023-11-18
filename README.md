# DM-Logger

## Urls

* [PyPI](https://pypi.org/project/dm-logger/)
* [GitHub](https://github.com/DIMKA4621/dm-logger)

## Parameters

* Class options

   ```python
         logs_dir_path: str = "logs"  # log parent directories, leave blank to not write
             file_name: str = ""  # log file name, default = <name>.log
            write_mode: Literal["a", "w"] = "w"  # start with new file or continue old one
                max_MB: int = 5  # max log file size (MB)
             max_count: int = 10  # max count of saved logs
       show_name_label: bool = False  # show logger name in the log message or not
   show_location_label: Optional[bool] = False  # show location in the log message or not: True - anywhere, False - only for ERROR and CRITICAL, None - not
         format_string: str = "%(asctime)s.%(msecs)03d [%(levelname)s] (%(module)s.%(funcName)s:%(lineno)d) %(message)s"
   ```

* Init parameters

   ```python
            name: str  # logger name (*required)
   logging_level: str = "DEBUG"  # min logging level
      write_logs: bool = True  # write to file or not
      print_logs: bool = True  # print to the console or not
   ```

## Usage

### Setup class options

_This options usage for all loggers_

```python
from dm_logger import DMLogger

DMLogger.options.show_name_label = True
DMLogger.options.max_count = 5
```

### Record

```python
from dm_logger import DMLogger

logger = DMLogger("main")

logger.info("test message", tag="test tag")
logger.debug("new message", id=123312)
logger.info("only mess")
logger.critical(env="production")
logger.warning({"key": "value"})
logger.error(["item1", "item2", 3])
logger.info()
```

### Several loggers

_All loggers will write to one file_

```python
from dm_logger import DMLogger

DMLogger.options.show_name_label = True

logger = DMLogger("main", level="INFO")
debugger = DMLogger("debugger", print_logs=False)

logger.info("Start app")
debugger.debug(process_id=123123)
logger.error("App crashed!")
```

Output

```text
16-11-2023 18:05:26.581 [INFO] [main] -- Start app
16-11-2023 18:05:26.582 [ERROR] [main] -- App crashed!
```

Log file

```text
16-11-2023 18:04:06.402 [INFO] [main] -- Start app
16-11-2023 18:04:06.402 [DEBUG] [logger_2] {process_id: 123123}
16-11-2023 18:04:06.402 [ERROR] [main] -- App crashed!
```

## Requirements

Python 3.7 or higher.
