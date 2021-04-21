#!/usr/bin/env python3

from asyncio import run
from json import dump, load
from os import path, makedirs
from getpass import getpass

from nio import AsyncClient, AsyncClientConfig, LoginResponse, RoomMessageText, SyncResponse

from urllib import request
from lxml import html


async def send_message(content: dict, room_id: str, client: AsyncClient) -> None:
    if await is_in_room(room_id, client):
        await client.room_send(
            room_id,
            "m.room.message",
            content,
            ignore_unverified_devices=True
        )


async def join_room(room_id: str, client: AsyncClient) -> None:
    if not await is_in_room(room_id, client):
        await client.join(room_id)


async def leave_room(room_id: str, client: AsyncClient) -> None:
    if await is_in_room(room_id, client):
        await client.room_leave(room_id)


async def is_in_room(room_id: str, client: AsyncClient) -> bool:
    if room_id in await get_joined_rooms(client):
        return True
    return False


async def get_joined_rooms(client: AsyncClient) -> str:
    joined_rooms = await client.joined_rooms()
    return joined_rooms.rooms


async def get_credentials(user_id: str, device_id: str, home_server: str, store_path: str) -> LoginResponse:
    client_config = AsyncClientConfig(
        max_limit_exceeded=0,
        max_timeouts=0,
        store_sync_tokens=True,
        encryption_enabled=True,
    )
    client = AsyncClient(
        home_server,
        user_id,
        store_path=store_path,
        config=client_config
    )
    password = getpass()
    response = await client.login(password, device_name=device_id)
    await client.close()

    if (isinstance(response, LoginResponse)):
        return response
    return None


def save_credentials(user_id: str, device_id: str, home_server: str, access_token: str, path: str) -> None:
    with open(path, "w") as file:
        dump(
            {
                "homeserver": home_server,
                "user_id": user_id,
                "device_id": device_id,
                "access_token": access_token
            },
            file
        )


def get_client(user_id: str, device_id: str, home_server: str, access_token: str, store_path: str) -> AsyncClient:
    client_config = AsyncClientConfig(
        max_limit_exceeded=0,
        max_timeouts=0,
        store_sync_tokens=True,
        encryption_enabled=True,
    )
    client = AsyncClient(
        home_server,
        user_id,
        device_id=device_id,
        store_path=store_path,
        config=client_config
    )
    client.restore_login(
        user_id=user_id,
        device_id=device_id,
        access_token=access_token
    )
    return client


def get_bot_config(path: str) -> str:
    if does_file_exists(path):
        with open(path, "r") as file:
            return load(file)
    return None


def load_credentials(path: str) -> str:
    if does_file_exists(path):
        with open(path, "r") as file:
            return load(file)
    return None


def does_file_exists(file_path: str) -> bool:
    if path.exists(file_path):
        return True
    return False


async def main() -> None:
    credentials_path = "credentials.json"
    store_path = "store"
    bot_path = "bot.json"
    bot_config = get_bot_config(bot_path)
    news_path = "news.txt"

    if not path.exists(store_path):
        makedirs(store_path)

    if bot_config is None:
        return

    if not does_file_exists(credentials_path):
        credentials = await get_credentials(
            bot_config["user_id"],
            bot_config["device_id"],
            bot_config["home_server"],
            store_path
        )
        save_credentials(
            credentials.user_id,
            credentials.device_id,
            bot_config["home_server"],
            credentials.access_token,
            credentials_path
        )

    credentials = load_credentials(credentials_path)
    client = get_client(
        bot_config["user_id"],
        bot_config["device_id"],
        bot_config["home_server"],
        credentials["access_token"],
        store_path
    )

    # await leave_room(bot_config["testing_room"], client)
    await join_room(bot_config["testing_room"], client)

    if client.should_upload_keys:
        await client.keys_upload()

    sync = await client.sync(timeout=30000, full_state=True)
    links = await get_room_links(bot_config["testing_room"], sync, client)
    y_news = get_y_news(links)

    if y_news is not None:
        await send_message(
            {
                "msgtype": "m.text",
                "body": y_news
            },
            bot_config["testing_room"],
            client
        )

    links = await get_room_links(bot_config["testing_room"], sync, client)
    the_hacker_news = get_the_hacker_news(links)

    if the_hacker_news is not None:
        await send_message(
            {
                "msgtype": "m.text",
                "body": the_hacker_news
            },
            bot_config["testing_room"],
            client
        )

    await client.close()


async def get_room_links(room_id: str, sync: SyncResponse, client: AsyncClient) -> list:
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


def get_the_hacker_news(existing_links: list) -> str:
    news = []
    resource = request.urlopen("https://thehackernews.com/")
    page = html.fromstring(resource.read().decode(
        resource.headers.get_content_charset()))

    for link in page.xpath("//a[@class='story-link']"):
        title = link.xpath(".//h2[@class='home-title']")[0].text
        link = link.get("href")

        if link in existing_links:
            continue

        news.append(f"{title}\n{link}")

    if len(news) <= 0:
        return None

    news.insert(0, "The Hacker News")
    news.append("\n")
    return "\n\n".join(news)


def get_y_news(existing_links: list) -> str:
    news = []
    resource = request.urlopen("https://news.ycombinator.com/")
    page = html.fromstring(resource.read().decode(
        resource.headers.get_content_charset()))

    for link in page.xpath("//a[@class='storylink']"):
        title = link.text
        link = link.get("href")

        if link in existing_links:
            continue

        news.append(f"{title}\n{link}")

    if len(news) <= 0:
        return None

    news.insert(0, "Hacker News")
    news.append("\n")
    return "\n\n".join(news)


if __name__ == "__main__":
    try:
        run(main())

    except KeyboardInterrupt:
        pass
