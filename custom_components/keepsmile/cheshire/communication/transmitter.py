import asyncio
from abc import ABC, abstractmethod

from ..generic.platform_command import PlatformCommand

class Transmitter(ABC):
    @abstractmethod
    async def close(self):
        """Must be called before transmitter is discarded so it can close connections etc."""
        pass

    @abstractmethod
    async def send_raw(self, raw_cmd: bytes):
        pass

    async def send(self, cmd: PlatformCommand):
        return await self.send_raw(cmd.get_bytes())
    
    async def send_all(self, cmds: list[PlatformCommand]):
        for cmd in cmds:
            await self.send(cmd)
            # FIX: Add a 100ms delay to prevent the BLE chip from dropping packets
            await asyncio.sleep(0.1)