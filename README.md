# Matrix Bot

A small and simple bot built with [Matrix Nio](https://github.com/poljar/matrix-nio). Currently, it can fetch send RSS feed updates to different rooms.

## Motivation
As privacy continues to degrade and companies who have amassed an enormous amount of user data continue to be hacked and leaked, the question of who we should trust our data with and what should they have access to is brought back into the spotlight.

As an experiment, is it feasible to move and use my daily activities such as emails, news, and calendar reminders into an end-to-end encrypted service such as Matrix?

Other solutions do exist such as IPFS, but that project is in a state that does not provide adequate privacy features such as E2EE.

The goal of this project is to provide privacy. Anonymity is probably a result of my Matrix accounts holding no links (email addresses, phone numbers, .etc) to identifiable information. But it is hosted on a VPS server which does hold personal information. As such anonymity is not guaranteed.

## Setup
### Dependenices:
- Python 3
- [Matrix Nio](https://github.com/poljar/matrix-nio)
- Feedparser

### Installing dependencies:
```
$ sudo apt install libolm-dev
$ pip3 install "matrix-nio[e2e]" feedparser
```

### Creating the config file:
All settings are stored in config.json. This file needs to be in the same directory as the other *.py files.

Below is an example of a basic config.json:
```json
{
    "bot": {
        "user_id": "@bot:example.com",
        "device_name": "matrix-container",
        "device_id": "",
        "home_server": "https://example.com",
        "access_token": "",
        "store_path": "store",
        "rooms": {
            "tech_news_room": "!EXAMPLE:example.com",
            "science_news_room": "!EXAMPLE:example.com"
        }
    },
    "news": {
        "hacker_news": {
            "url": "https://news.ycombinator.com/rss",
            "room": "tech_news_room"
        },
        "the_hacker_news": {
            "url": "https://feeds.feedburner.com/TheHackersNews?format=xml",
            "room": "tech_news_room"
        },
        "ars_technica_science": {
            "url": "https://feeds.arstechnica.com/arstechnica/science",
            "room": "science_news_room"
        }
    }
}
```

To add more RSS sources you'll need to add the following to `news` to the config:
```json
"example_news": {
    "url": "https://example.com/rss",
    "room": "example_news_room"
}
```

To add a new room, you'll need to add the following to `rooms`:
```json
"example_news_room": "!EXAMPLE:example.com"
```

So the config will look as follows if you added a new RSS source and room:
```json
{
    "bot": {
        "user_id": "@bot:example.com",
        "device_name": "matrix-container",
        "device_id": "",
        "home_server": "https://example.com",
        "access_token": "",
        "store_path": "store",
        "rooms": {
            "tech_news_room": "!EXAMPLE:example.com",
            "science_news_room": "!EXAMPLE:example.com",
            "example_news_room": "!EXAMPLE:example.com"
        }
    },
    "news": {
        "hacker_news": {
            "url": "https://news.ycombinator.com/rss",
            "room": "tech_news_room"
        },
        "the_hacker_news": {
            "url": "https://feeds.feedburner.com/TheHackersNews?format=xml",
            "room": "tech_news_room"
        },
        "ars_technica_science": {
            "url": "https://feeds.arstechnica.com/arstechnica/science",
            "room": "science_news_room"
        },
        "example_news": {
            "url": "https://example.com/rss",
            "room": "example_news_room"
        }
    }
}
```

Notice that `device_id` and `access_token` is empty, this will be filled later when we log in.

### Logging In

Now we need to log in, to do that you'll need to run the following command:
```
python3 login.py
```

### Join Rooms
Currently, join_room.py does not work consistently. To join a room, invite the bot to the room. Then login with the bot's credentials and accept the invite using the client such as a web browser.

### Verfying The Session
To verify the session, we need to run the following command:
```
python3 verify.py
```

### Running the bot
Currently, I have a cron task that runs every 30 minutes:
```
# crontab -e

*/30 * * * * /usr/bin/python3 /home/bot/matrix_bot/main.py >> /var/log/bot.log 2>&1
```

### Roadmap
- Fix join_room.py.
- Add proper error checks and handling errors (yes, I know, I am lazy).
- Add the ability to add calendar reminders.
- Can emails be converted into a chat application format? Is it even a good idea?