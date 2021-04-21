#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import getpass

from nio import AsyncClient, AsyncClientConfig, LoginResponse


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


async def get_credentials(user_id: str, device_id: str, home_server: str, store_path: str):
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
    password = getpass.getpass()
    response = await client.login(password, device_name=device_id)
    await client.close()

    if (isinstance(response, LoginResponse)):
        return response
    return None


def save_credentials(user_id: str, device_id: str, home_server: str, access_token: str, path: str) -> None:
    with open(path, "w") as file:
        json.dump(
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


def get_bot_config(path: str):
    if does_file_exists(path):
        with open(path, "r") as file:
            return json.load(file)
    return None


def load_credentials(path: str):
    if does_file_exists(path):
        with open(path, "r") as file:
            return json.load(file)
    return None


def does_file_exists(path: str) -> bool:
    if os.path.exists(path):
        return True
    return False


async def main() -> None:
    credentials_path = "credentials.json"
    store_path = "store"
    bot_path = "bot.json"
    bot_config = get_bot_config(bot_path)

    if not os.path.exists(store_path):
        os.makedirs(store_path)

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

    await join_room(bot_config["testing_room"], client)

    if client.should_upload_keys:
        await client.keys_upload()

    await client.sync(timeout=30000, full_state=True)

    await send_message(
        {
            "msgtype": "m.text",
            "body": "Google\nhttps://www.google.com.au"
        },
        bot_config["testing_room"],
        client
    )

    await client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
