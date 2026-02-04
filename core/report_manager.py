import asyncio
import logging
from typing import List, Dict
from pyrogram import Client
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import *
from utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class ReportManager:
    """举报管理器"""
    
    # 举报原因映射
    REASON_MAP = {
        1: ("child_abuse", InputReportReasonChildAbuse()),
        2: ("copyright", InputReportReasonCopyright()),
        3: ("impersonation", InputReportReasonFake()),
        4: ("geo_irrelevant", InputReportReasonGeoIrrelevant()),
        5: ("illegal_drugs", InputReportReasonIllegalDrugs()),
        6: ("violence", InputReportReasonViolence()),
        7: ("spam", InputReportReasonSpam()),
        8: ("pornography", InputReportReasonPornography()),
        9: ("personal_details", InputReportReasonPersonalDetails())
    }
    
    def __init__(self, cooldown: int = 5):
        self.rate_limiter = RateLimiter(cooldown)
    
    def get_reason(self, choice: int):
        """获取举报原因"""
        return self.REASON_MAP.get(choice, (None, None))
    
    async def validate_target(self, client: Client, target: str) -> bool:
        """验证目标"""
        try:
            await client.get_chat(target)
            return True
        except Exception as e:
            logger.error(f"Invalid target {target}: {e}")
            return False
    
    async def report_target(
        self,
        session_string: str,
        target: str,
        reason_choice: int,
        message: str = ""
    ) -> Dict:
        """举报目标"""
        reason_name, reason_obj = self.get_reason(reason_choice)
        if not reason_obj:
            return {"success": False, "error": "Invalid reason choice"}
        
        try:
            async with Client(
                name="report_session",
                session_string=session_string,
                in_memory=True
            ) as client:
                # 等待频率限制
                await self.rate_limiter.wait()
                
                # 验证目标
                if not await self.validate_target(client, target):
                    return {"success": False, "error": "Invalid target"}
                
                # 解析目标
                peer = await client.resolve_peer(target)
                
                # 创建举报请求
                if hasattr(peer, 'channel_id'):
                    input_peer = InputPeerChannel(
                        channel_id=peer.channel_id,
                        access_hash=peer.access_hash
                    )
                elif hasattr(peer, 'user_id'):
                    input_peer = InputPeerUser(
                        user_id=peer.user_id,
                        access_hash=peer.access_hash
                    )
                else:
                    return {"success": False, "error": "Unsupported peer type"}
                
                # 发送举报
                report = ReportPeer(
                    peer=input_peer,
                    reason=reason_obj,
                    message=message
                )
                
                result = await client.invoke(report)
                return {
                    "success": True,
                    "result": result,
                    "reason": reason_name
                }
                
        except FloodWait as e:
            wait_time = e.value
            logger.warning(f"Flood wait for {wait_time} seconds")
            await asyncio.sleep(wait_time)
            return {"success": False, "error": f"Flood wait: {wait_time}s"}
        except Exception as e:
            logger.error(f"Report failed: {e}")
            return {"success": False, "error": str(e)}
