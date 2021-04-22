#!/usr/bin/env python3

from asyncio import run
import json
from os import path, makedirs
from getpass import getpass

from nio import Client, ClientConfig, LoginResponse, RoomMessageText, SyncResponse

from urllib import request
from feedparser import parse



async def get_room_links(room_id: str, sync: SyncResponse, client: Client) -> list:
    links = []
    start = sync.next_batch

    while True:
        messages = await client.room_messages(room_id, start)

        if start == messages.end:
            break

        start = messages.end

        for text in messages.chunk:
            if isinstance(text, RoomMessageText):
                for line in str(text).split('\n'):
                    if line.startswith("https://"):
                        links.append(line)

    return links


def get_the_hacker_news(existing_links: list) -> (str, list):
    news = []
    new_links = []
    data = parse("https://feeds.feedburner.com/TheHackersNews?format=xml")

    for entry in data.entries:
        title = entry.title
        link = entry.link.replace("http://", "https://")

        if link in existing_links:
            continue

        news.append(f"{title}\n{link}")
        new_links.append(link)

    new_links += existing_links

    if len(news) <= 0:
        return (None, new_links)

    news.insert(0, data.feed.title)
    news.append("\n")

    return ("\n\n".join(news), new_links)


def get_y_news(existing_links: list) -> (str, list):
    news = []
    new_links = []
    data = parse("https://news.ycombinator.com/rss")

    for entry in data.entries:
        title = entry.title
        link = entry.comments

        if link in existing_links:
            continue

        news.append(f"{title}\n{link}")
        new_links.append(link)

    new_links += existing_links

    if len(news) <= 0:
        return (None, new_links)

    news.insert(0, data.feed.title)
    news.append("\n")

    return ("\n\n".join(news), new_links)


def get_ars_technica_news(existing_links: list) -> (str, list):
    news = []
    new_links = []
    data = parse("https://feeds.arstechnica.com/arstechnica/science")

    for entry in data.entries:
        title = entry.title
        link = entry.link.replace("http://", "https://")

        if link in existing_links:
            continue

        news.append(f"{title}\n{link}")
        new_links.append(link)

    new_links += existing_links

    if len(news) <= 0:
        return (None, new_links)

    news.insert(0, data.feed.title)
    news.append("\n")

    return ("\n\n".join(news), new_links)


async def send_science_news(bot_config: dict, sync: SyncResponse, client: Client) -> None:
    news = ""
    room_id = bot_config["science_news_room"]

    links = await get_room_links(room_id, sync, client)

    ars_technica_news, new_links = get_ars_technica_news(links)
    # the_hacker_news, new_links = get_the_hacker_news(new_links)

    if ars_technica_news is not None:
        news += ars_technica_news

    # if the_hacker_news is not None:
    #     news += the_hacker_news

    if len(news) <= 0:
        return

    await send_message(news, room_id, client)


async def send_tech_news(bot_config: dict, sync: SyncResponse, client: Client) -> None:
    news = ""
    room_id = bot_config["tech_news_room"]

    links = await get_room_links(room_id, sync, client)

    y_news, new_links = get_y_news(links)
    the_hacker_news, new_links = get_the_hacker_news(new_links)

    if y_news is not None:
        news += y_news

    if the_hacker_news is not None:
        news += the_hacker_news

    if len(news) <= 0:
        return

    await send_message(news, room_id, client)


async def main() -> None:
    bot = Bot("config.json")

    print()

    # try:
    #     if client.should_upload_keys:
    #         await client.keys_upload()

    #     sync = await client.sync(timeout=30000, full_state=True)

    #     # await send_tech_news(bot_config, sync, client)
    #     await send_science_news(bot_config, sync, client)

    # finally:
    #     await client.close()


if __name__ == "__main__":
    bot = Bot("config.json")
    print()
