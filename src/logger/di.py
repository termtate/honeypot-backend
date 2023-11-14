from injector import singleton, provider, Module
from loguru import logger
from loguru._logger import Logger


class LoggerModule(Module):
    @singleton
    @provider
    def provide_logger(self) -> Logger:
        logger.add(
            "log/received.log",
            retention="1 week",  # 保留最新一周数据
            rotation="10 MB"  # 超过10mb创建新文件
        )
        return logger  # type: ignore
