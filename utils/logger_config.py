import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

class ZoneInfoFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, timezone="Asia/Seoul"):
        super().__init__(fmt, datefmt)
        self.tz = ZoneInfo(timezone)

    def converter(self, timestamp):
        return datetime.fromtimestamp(timestamp, tz=self.tz)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

def setup_logging():
    root_logger = logging.getLogger()
    
    # 중요: 기존에 붙어있는 핸들러가 있다면 모두 제거 (설정 꼬임 방지)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = ZoneInfoFormatter(
        fmt='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        timezone="Asia/Seoul"
    )
    handler.setFormatter(formatter)
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    
    return root_logger
