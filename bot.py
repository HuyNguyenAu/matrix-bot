#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import getpass

from nio import AsyncClient, LoginResponse


async def send_message(content: dict, room_id: str, client: AsyncClient) -> None:
    if await is_in_room(room_id, client):
        await client.room_send(
            room_id,
            message_type="m.room.message",
            content=content
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


async def get_credentials(user_id: str, device_id: str, home_server: str):
    client = AsyncClient(home_server, user_id)
    password = getpass.getpass()
    response = await client.login(password, device_id)
    await client.close()
    return response


def save_credentials(path: str, response: LoginResponse, home_server: str) -> None:
    with open(path, "w") as file:
        json.dump(
            {
                "homeserver": home_server,
                "user_id": response.user_id,
                "device_id": response.device_id,
                "access_token": response.access_token
            },
            file
        )


def get_client(user_id: str, device_id: str, home_server: str, access_token: str) -> AsyncClient:
    client = AsyncClient(home_server)
    client.access_token = access_token
    client.user_id = user_id
    client.device_id = device_id
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
    bot_path = "bot.json"
    bot_config = get_bot_config(bot_path)

    if bot_config is None:
        return

    if not does_file_exists(credentials_path):
        credentials = await get_credentials(
            bot_config["user_id"],
            bot_config["device_id"],
            bot_config["home_server"]
        )
        save_credentials(
            credentials_path,
            credentials,
            bot_config["home_server"]
        )

    credentials = load_credentials(credentials_path)
    client = get_client(
        bot_config["user_id"],
        bot_config["device_id"],
        bot_config["home_server"],
        credentials["access_token"])

    await send_message(
        {
            "msgtype": "m.text",
            "body": "Hello world!"
        },
        bot_config["testing_room"],
        client
    )

    await client.close()

asyncio.get_event_loop().run_until_complete(main())
