from injector import singleton, provider, Module
from loguru import logger

from typing import Protocol, runtime_checkable


@runtime_checkable
class Logger(Protocol):
    def info(self, content: object):
        ...

    def warning(self, content: object):
        ...

    def debug(self, content: object):
        ...

    def error(self, content: object):
        ...

    def critical(self, content: object):
        ...

    def success(self, content: object):
        ...


class LoggerModule(Module):
    @singleton
    @provider
    def provide_logger(self) -> Logger:
        # https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
        logger.add(
            "log/received_{time}.log",
            retention="1 week",  # 保留最新一周数据
            rotation="10 MB",  # 超过10mb创建新文件
        )
        return logger  # type: ignore
