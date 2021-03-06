#!/usr/bin/env python3

from config import Config

import nio
import asyncio


class Bot:
    def __init__(self, config: Config, sync: bool = True):
        self.__client_config = nio.AsyncClientConfig(
            max_limit_exceeded=0,
            max_timeouts=0,
            store_sync_tokens=True,
            encryption_enabled=True,
        )
        self.__config = config
        self.__client = self.__load_client()
        self.__sync_keys()
        self.__sync = None

        if sync:
            self.__sync = self.__sync_state()

    def get_client(self) -> nio.AsyncClient:
        return self.__client

    def join_room(self, room_id: str) -> None:
        if not self.__is_in_room(room_id):
            asyncio.get_event_loop().run_until_complete(
                self.__client.join(room_id)
            )

    def get_rooms(self) -> dict:
        return self.__config.get_rooms()

    def get_room_links(self, room_id: str) -> list:
        links = []
        start = self.__sync.next_batch

        while True:
            messages = asyncio.get_event_loop().run_until_complete(
                self.__client.room_messages(room_id, start)
            )

            if start == messages.end:
                break

            start = messages.end

            for text in messages.chunk:
                if isinstance(text, nio.RoomMessageText):
                    for line in str(text).split('\n'):
                        if line.startswith("https://"):
                            links.append(line)

        return links

    def close_client(self) -> None:
        asyncio.get_event_loop().run_until_complete(self.__client.close())

    def send_message(self, content: str, room_id: str) -> None:
        if self.__is_in_room(room_id):
            asyncio.get_event_loop().run_until_complete(
                self.__client.room_send(
                    room_id=room_id,
                    message_type="m.room.message",
                    content={
                        "msgtype": "m.text",
                        "body": content
                    },
                    ignore_unverified_devices=True
                )
            )

    def __load_client(self) -> nio.AsyncClient:
        client = nio.AsyncClient(
            homeserver=self.__config.get_home_server(),
            user=self.__config.get_user_id(),
            device_id=self.__config.get_device_id(),
            store_path=self.__config.get_store_path(),
            config=self.__client_config,
            ssl=True
        )
        client.restore_login(
            user_id=self.__config.get_user_id(),
            device_id=self.__config.get_device_id(),
            access_token=self.__config.get_access_token()
        )

        return client

    def __sync_keys(self) -> None:
        if self.__client.should_upload_keys:
            asyncio.get_event_loop().run_until_complete(self.__client.keys_upload())

    def __sync_state(self) -> nio.SyncResponse:
        return asyncio.get_event_loop().run_until_complete(self.__client.sync(
            timeout=30000,
            full_state=True
        ))


    def __is_in_room(self, room_id: str) -> bool:
        if room_id in self.__get_joined_rooms():
            return True
        return False

    def __get_joined_rooms(self) -> list:
        response = asyncio.get_event_loop().run_until_complete(self.__client.joined_rooms())
        return response.rooms
