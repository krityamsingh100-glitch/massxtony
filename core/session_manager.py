import json
import asyncio
import logging
from typing import List, Dict, Optional
from pathlib import Path
from pyrogram import Client
from pyrogram.errors import (
    SessionExpired, 
    AuthKeyDuplicated, 
    FloodWait
)

logger = logging.getLogger(__name__)

class SessionManager:
    """会话管理器"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.sessions: List[Dict] = []
        self.load_config()
    
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.sessions = config.get('accounts', [])
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return False
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            config = {"accounts": self.sessions}
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    async def validate_session(self, session_string: str) -> Optional[Dict]:
        """验证会话字符串"""
        try:
            async with Client(
                name="temp_session",
                session_string=session_string,
                in_memory=True
            ) as app:
                user = await app.get_me()
                return {
                    "id": user.id,
                    "first_name": user.first_name,
                    "username": user.username,
                    "session_string": session_string,
                    "is_bot": user.is_bot
                }
        except SessionExpired:
            logger.warning("Session expired")
            return None
        except AuthKeyDuplicated:
            logger.warning("Session is being used elsewhere")
            return None
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return None
    
    async def add_session(self, session_string: str) -> bool:
        """添加新会话"""
        # 检查是否已存在
        for session in self.sessions:
            if session['session_string'] == session_string:
                logger.warning("Session already exists")
                return False
        
        # 验证会话
        user_info = await self.validate_session(session_string)
        if not user_info:
            return False
        
        # 添加到列表
        self.sessions.append(user_info)
        return self.save_config()
    
    def remove_session(self, user_id: int) -> bool:
        """移除会话"""
        self.sessions = [s for s in self.sessions if s['id'] != user_id]
        return self.save_config()
    
    def get_sessions(self) -> List[Dict]:
        """获取所有会话"""
        return self.sessions.copy()
    
    def get_session_count(self) -> int:
        """获取会话数量"""
        return len(self.sessions)
