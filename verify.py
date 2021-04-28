#!/usr/bin/env python3

from config import Config
from bot import Bot

import traceback
import getpass
import sys
import os
import json
import asyncio
import nio


async def main(client: nio.AsyncClient):
    # Set up event callbacks
    callbacks = Callbacks(client)
    client.add_to_device_callback(callbacks.to_device_callback, (nio.KeyVerificationEvent,))
    # Sync encryption keys with the server
    # Required for participating in encrypted rooms
    if client.should_upload_keys:
        await client.keys_upload()
    print(
        "This program is ready and waiting for the other party to initiate "
        'an emoji verification with us by selecting "Verify by Emoji" '
        "in their Matrix client."
    )
    await client.sync_forever(timeout=30000, full_state=True)

class Callbacks(object):
    def __init__(self, client):
        self.client = client

    async def to_device_callback(self, event):  # noqa
        try:
            client = self.client

            if isinstance(event, nio.KeyVerificationStart):  # first step
                if "emoji" not in event.short_authentication_string:
                    print(
                        "Other device does not support emoji verification "
                        f"{event.short_authentication_string}."
                    )
                    return
                resp = await client.accept_key_verification(event.transaction_id)
                if isinstance(resp, nio.ToDeviceError):
                    print(f"accept_key_verification failed with {resp}")

                sas = client.key_verifications[event.transaction_id]

                todevice_msg = sas.share_key()
                resp = await client.to_device(todevice_msg)
                if isinstance(resp, nio.ToDeviceError):
                    print(f"to_device failed with {resp}")

            elif isinstance(event, nio.KeyVerificationCancel):  # anytime
                # There is no need to issue a
                # client.cancel_key_verification(tx_id, reject=False)
                # here. The SAS flow is already cancelled.
                # We only need to inform the user.
                print(
                    f"Verification has been cancelled by {event.sender} "
                    f'for reason "{event.reason}".'
                )

            elif isinstance(event, nio.KeyVerificationKey):  # second step
                sas = client.key_verifications[event.transaction_id]

                print(f"{sas.get_emoji()}")

                yn = input("Do the emojis match? (Y/N) (C for Cancel) ")
                if yn.lower() == "y":
                    print(
                        "Match! The verification for this " "device will be accepted."
                    )
                    resp = await client.confirm_short_auth_string(event.transaction_id)
                    if isinstance(resp, nio.ToDeviceError):
                        print(f"confirm_short_auth_string failed with {resp}")
                elif yn.lower() == "n":  # no, don't match, reject
                    print(
                        "No match! Device will NOT be verified "
                        "by rejecting verification."
                    )
                    resp = await client.cancel_key_verification(
                        event.transaction_id, reject=True
                    )
                    if isinstance(resp, nio.ToDeviceError):
                        print(f"cancel_key_verification failed with {resp}")
                else:  # C or anything for cancel
                    print("Cancelled by user! Verification will be " "cancelled.")
                    resp = await client.cancel_key_verification(
                        event.transaction_id, reject=False
                    )
                    if isinstance(resp, nio.ToDeviceError):
                        print(f"cancel_key_verification failed with {resp}")

            elif isinstance(event, nio.KeyVerificationMac):  # third step
                sas = client.key_verifications[event.transaction_id]
                try:
                    todevice_msg = sas.get_mac()
                except nio.LocalProtocolError as e:
                    # e.g. it might have been cancelled by ourselves
                    print(
                        f"Cancelled or protocol error: Reason: {e}.\n"
                        f"Verification with {event.sender} not concluded. "
                        "Try again?"
                    )
                else:
                    resp = await client.to_device(todevice_msg)
                    if isinstance(resp, nio.ToDeviceError):
                        print(f"to_device failed with {resp}")
                    print(
                        f"sas.we_started_it = {sas.we_started_it}\n"
                        f"sas.sas_accepted = {sas.sas_accepted}\n"
                        f"sas.canceled = {sas.canceled}\n"
                        f"sas.timed_out = {sas.timed_out}\n"
                        f"sas.verified = {sas.verified}\n"
                        f"sas.verified_devices = {sas.verified_devices}\n"
                    )
                    print(
                        "Emoji verification was successful!\n"
                        "Hit Control-C to stop the program or "
                        "initiate another Emoji verification from "
                        "another device or room."
                    )
            else:
                print(
                    f"Received unexpected event type {type(event)}. "
                    f"Event is {event}. Event will be ignored."
                )
        except BaseException:
            print(traceback.format_exc())

if __name__ == "__main__":
    config = Config()
    bot = Bot(config)

    try:
        asyncio.get_event_loop().run_until_complete(main(bot.get_client()))
    finally:
        bot.close_client()
