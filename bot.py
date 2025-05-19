import logging
import logging.config
from typing import Union, AsyncGenerator

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

from pyrogram import Client, __version__, types
from pyrogram.raw.all import layer
from pyrogram import utils
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR
from utils import temp

# Monkey-patch get_peer_type for newer Pyrogram behavior
def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"

utils.get_peer_type = get_peer_type_new


class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset_id: int = 0,
    ) -> AsyncGenerator[types.Message, None]:
        """
        Internal bot method to iterate messages.
        DO NOT use this for fetching history because bots cannot call get_chat_history.
        Use the userbot client for that instead.
        """
        async for message in self.get_chat_history(chat_id, limit=limit, offset_id=offset_id):
            yield message


# User client for user-only methods like get_chat_history
userbot = Client(
    "user_session",  # user session file must be created beforehand
    api_id=API_ID,
    api_hash=API_HASH,
    workers=50,
)


async def start_userbot():
    await userbot.start()
    logging.info("Userbot started for fetching history and user-only methods.")


async def stop_userbot():
    await userbot.stop()
    logging.info("Userbot stopped.")


async def get_history_with_userbot(chat_id: Union[int, str], limit: int, offset_id: int = 0):
    messages = []
    try:
        async for msg in userbot.get_chat_history(chat_id, limit=limit, offset_id=offset_id):
            messages.append(msg)
    except Exception as e:
        logging.error(f"Failed to get history with userbot: {e}")
    return messages


bot_app = Bot()


async def main():
    await bot_app.start()
    await start_userbot()

    # Example usage:
    # msgs = await get_history_with_userbot(chat_id=123456789, limit=10)
    # logging.info(f"Fetched {len(msgs)} messages from userbot")

    await bot_app.idle()

    await stop_userbot()
    await bot_app.stop()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
