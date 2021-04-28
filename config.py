#!/usr/bin/env python3

import json


class Config:
    def __init__(self):
        path = "config.json"
        config = self.__load_config(path)

        self.__user_id = config["bot"]["user_id"]
        self.__device_name = config["bot"]["device_name"]
        self.__device_id = config["bot"]["device_id"]
        self.__home_server = config["bot"]["home_server"]
        self.__access_token = config["bot"]["access_token"]
        self.__rooms = config["bot"]["rooms"]
        self.__store_path = config["bot"]["store_path"]
        self.__news = self.__load_news(config["news"])

    def get_user_id(self) -> str:
        return self.__user_id

    def get_device_name(self) -> str:
        return self.__device_name

    def get_device_id(self) -> str:
        return self.__device_id

    def set_device_id(self, device_id: str) -> str:
        self.__device_id = device_id

    def get_home_server(self) -> str:
        return self.__home_server

    def get_access_token(self) -> str:
        return self.__access_token

    def set_access_token(self, access_token: str) -> None:
        self.__access_token = access_token

    def get_rooms(self) -> dict:
        return self.__rooms

    def get_room_id(self, room_key: str) -> dict:
        return self.__rooms[room_key]

    def get_news(self) -> list:
        return self.__news

    def get_store_path(self) -> str:
        return self.__store_path

    def save_config(self) -> str:
        with open("config.json", "w") as file:
            return json.dump(
                obj={
                    "bot": {
                        "user_id": self.__user_id,
                        "device_name": self.__device_name,
                        "device_id": self.__device_id,
                        "home_server": self.__home_server,
                        "access_token": self.__access_token,
                        "store_path": self.__store_path,
                        "rooms": self.__rooms
                    },
                    "news": self.__news
                },
                fp=file)

    def __load_config(self, path: str) -> dict:
        with open(path, "r") as file:
            return json.load(file)

    def __load_news(self, news: dict) -> list:
        news_list = []

        for source in news:
            news_item = news[source]

            news_list.append(
                News(
                    news_item["url"],
                    news_item["room"]
                )
            )

        return news_list


class News:
    def __init__(self, url: str, room: str):
        self.__url = url
        self.__room = room

    def get_url(self):
        return self.__url

    def get_room(self):
        return self.__room
