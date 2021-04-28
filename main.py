#!/usr/bin/env python3

from config import Config
from bot import Bot

import asyncio
import feedparser


def get_rss_news(url: str, existing_links: list) -> str:
    news = []
    new_links = []
    data = feedparser.parse(url)

    for entry in data.entries:
        title = entry.title
        link = entry.link.replace("http://", "https://")

        if link in existing_links:
            continue

        news.append(f"{title}\n{link}")
        new_links.append(link)

    if len(news) <= 0:
        return None

    news.insert(0, data.feed.title)
    news.append("\n")

    return "\n\n".join(news)


def send_news(bot: Bot, config: Config):
    for news_item in config.get_news():
        room_id = config.get_room_id(
            news_item.get_room()
        )
        news = get_rss_news(
            url=news_item.get_url(),
            existing_links=bot.get_room_links(room_id)
        )

        if news == None:
            continue

        bot.send_message(
            content=news,
            room_id=room_id
        )


if __name__ == "__main__":
    config = Config()
    bot = Bot(config)

    try:
        send_news(bot=bot, config=config)
    finally:
        bot.close_client()
