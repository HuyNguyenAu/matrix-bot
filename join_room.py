#!/usr/bin/env python3

import sys
import asyncio

from config import Config
from bot import Bot

async def main() -> None:
    room_id = sys.argv[1]
    config = Config()
    bot = Bot(config)

    try:
        await bot.join_room(room_id)
    finally:
        await bot.close_client()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
