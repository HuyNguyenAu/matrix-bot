from config import Config

import nio


class Bot:
    def __init__(self, config: Config):
        self.__client_config = nio.AsyncClientConfig(
            max_limit_exceeded=0,
            max_timeouts=0,
            store_sync_tokens=True,
            encryption_enabled=True,
        )
        self.__config = config
        self.__client = self.__load_client()
        self.__sync = None

    def get_client(self) -> nio.AsyncClient:
        return self.__client

    def get_sync(self) -> nio.SyncResponse:
        return self.__sync

    async def join_room(self, room_id: str) -> None:
        if not await self.__is_in_room(room_id):
            await self.__client.join(room_id)

    async def close_client(self) -> None:
        await self.__client.close()

    async def send_message(self, content: str, room_id: str) -> None:
        if await self.__is_in_room(room_id):
            await self.__client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": content
                },
                ignore_unverified_devices=True
            )

    async def __sync(self) -> None:
        self.__sync = await self.__client.sync(timeout=30000, full_state=True)

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

    async def __is_in_room(self, room_id: str) -> bool:
        if room_id in await self.__get_joined_rooms():
            return True
        return False

    async def __get_joined_rooms(self) -> list:
        return (await self.__client.joined_rooms()).rooms
