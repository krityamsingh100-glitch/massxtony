import asyncio
import time
from typing import Optional

class RateLimiter:
    """频率限制器"""
    
    def __init__(self, cooldown: int = 5):
        self.cooldown = cooldown
        self.last_request: Optional[float] = None
    
    async def wait(self):
        """等待直到可以发送下一个请求"""
        if self.last_request is not None:
            elapsed = time.time() - self.last_request
            if elapsed < self.cooldown:
                wait_time = self.cooldown - elapsed
                await asyncio.sleep(wait_time)
        
        self.last_request = time.time()
