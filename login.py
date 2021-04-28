#!/usr/bin/env python3

import json
import sys
import getpass
import os
import nio
import asyncio
import traceback

from config import Config


async def main() -> None:
    config = Config()
    store_path = config.get_store_path()

    print(config.get_news_json())

    return

    if not os.path.exists(store_path):
        os.makedirs(store_path)

    if len(config.get_access_token()) > 0:
        print("Access token already set.")
        sys.exit(1)

    client_config = nio.AsyncClientConfig(
        max_limit_exceeded=0,
        max_timeouts=0,
        store_sync_tokens=True,
        encryption_enabled=True,
    )

    client = nio.AsyncClient(
        homeserver=config.get_home_server(),
        user=config.get_user_id(),
        store_path=config.get_store_path(),
        config=client_config,
        ssl=True
    )

    response = await client.login(
        password=getpass.getpass(),
        device_name=config.get_device_name()
    )
    await client.close()

    if not isinstance(response, nio.LoginResponse):
        print("Failed to get access token.")
        sys.exit(1)

    config.set_access_token(response.access_token)
    config.set_device_id(response.device_id)
    config.save_config()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except Exception:
        print(traceback.format_exc())
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
