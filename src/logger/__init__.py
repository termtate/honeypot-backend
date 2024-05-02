from loguru import logger

logger.add(
    "log/received_{time}.log",
    retention="1 week",  # 保留最新一周数据
    rotation="10 MB",  # 超过10mb创建新文件
)
