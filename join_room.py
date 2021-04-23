#!/usr/bin/env python3

import sys

from bot import Bot

if __name__ == "__main__":
    room_id = sys.argv[1]
    bot = Bot()
    bot.join_room(room_id)
    bot.close_client()
