#!/usr/bin/env python3

import sys

from config import Config
from bot import Bot

if __name__ == "__main__":
    room_id = sys.argv[1]
    bot = Bot(Config())
    bot.join_room(room_id)
    bot.close_client()
