import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class Config:
    """配置类"""
    
    # API配置
    API_ID: int = int(os.environ.get("API_ID", 0))
    API_HASH: str = os.environ.get("API_HASH", "")
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
    
    # 所有者配置
    OWNER_ID: int = int(os.environ.get("OWNER_ID", 0))
    
    # 限制配置
    REPORT_COOLDOWN: int = int(os.environ.get("REPORT_COOLDOWN", 5))
    MAX_ACCOUNTS: int = int(os.environ.get("MAX_ACCOUNTS", 10))
    MAX_REPORTS_PER_DAY: int = 400  # 每日最大举报次数
    
    # 路径配置
    CONFIG_PATH: str = "config.json"
    LOGS_PATH: str = "logs"
    
    # 验证配置
    @classmethod
    def validate(cls) -> bool:
        """验证配置"""
        errors = []
        
        if not cls.API_ID or cls.API_ID == 0:
            errors.append("API_ID is required")
        
        if not cls.API_HASH:
            errors.append("API_HASH is required")
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        
        if not cls.OWNER_ID or cls.OWNER_ID == 0:
            errors.append("OWNER_ID is required")
        
        if errors:
            for error in errors:
                logger.error(f"Config error: {error}")
            return False
        
        return True
    
    @classmethod
    def get_owner_ids(cls) -> list:
        """获取所有者ID列表"""
        return [cls.OWNER_ID]
