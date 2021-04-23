from config import Config

import nio
import asyncio


class Bot:
    def __init__(self):
        self.__client_config = nio.AsyncClientConfig(
            max_limit_exceeded=0,
            max_timeouts=0,
            store_sync_tokens=True,
            encryption_enabled=True,
        )
        self.__config = Config()
        self.__client = self.__load_client()
        self.__sync_keys()
        self.__sync = self.__sync_state()

    def get_client(self) -> nio.AsyncClient:
        return self.__client

    def get_sync(self) -> nio.SyncResponse:
        return self.__sync

    def join_room(self, room_id: str) -> None:
        if not self.__is_in_room(room_id):
            asyncio.get_event_loop().run_until_complete(self.__client.join(room_id))

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
        reponse = asyncio.get_event_loop().run_until_complete(self.__client.sync(
            timeout=30000, full_state=True))

        if not isinstance(reponse, nio.SyncResponse):
            return None

        return reponse

    def __is_in_room(self, room_id: str) -> bool:
        if room_id in self.__get_joined_rooms():
            return True
        return False

    def __get_joined_rooms(self) -> list:
        response = asyncio.get_event_loop().run_until_complete(self.__client.joined_rooms())
        return response.rooms