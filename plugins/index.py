import logging
import asyncio
import re
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import (
    ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
)
from info import ADMINS, INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    _, action, chat, lst_msg_id, from_user = query.data.split("#")
    if action == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been declined by our moderators.',
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('Wait until previous process completes.', show_alert=True)

    msg = query.message
    await query.answer('Processing...⏳', show_alert=True)

    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been accepted and will be added soon.',
                               reply_to_message_id=int(lst_msg_id))

    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
        )
    )

    try:
        chat = int(chat)
    except:
        pass

    await index_files_to_db(int(lst_msg_id), chat, msg, bot)

@Client.on_message(
    (filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text)
    & filters.private & filters.incoming
)
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
    elif message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return

    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('Private channel/group. Make me an admin to index files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'Error: {e}')

    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Ensure I am admin in the channel if private.')

    if k.empty:
        return await message.reply('Message not found or I am not an admin.')

    if message.from_user.id in ADMINS:
        buttons = [[
            InlineKeyboardButton('Yes', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
        ], [
            InlineKeyboardButton('close', callback_data='close_data'),
        ]]
        return await message.reply(
            f'Do you want to index this channel/group?\n\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>',
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    if isinstance(chat_id, int):
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('Ensure I am admin and have invite permission.')
    else:
        link = f"@{message.forward_from_chat.username}"

    buttons = [[
        InlineKeyboardButton('Accept Index', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
    ], [
        InlineKeyboardButton('Reject Index', callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}'),
    ]]
    await bot.send_message(
        LOG_CHANNEL,
        f'#IndexRequest\n\nBy: {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID: <code>{chat_id}</code>\nLast Msg ID: <code>{last_msg_id}</code>\nInvite Link: {link}',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await message.reply('Thanks for your contribution. Awaiting moderator review.')

@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if ' ' in message.text:
        _, skip = message.text.split(" ", 1)
        try:
            skip = int(skip)
        except:
            return await message.reply("Skip number should be an integer.")
        temp.CURRENT = skip
        return await message.reply(f"Successfully set SKIP number to {skip}")
    else:
        await message.reply("Usage: /setskip <number>")

async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0

    async with lock:
        try:
            current_msg_id = lst_msg_id
            temp.CANCEL = False

            while current_msg_id > 0:
                if temp.CANCEL:
                    await msg.edit(
                        f"Cancelled!\n\nSaved: <code>{total_files}</code>\nDuplicates: <code>{duplicate}</code>\n"
                        f"Deleted: <code>{deleted}</code>\nNo Media: <code>{no_media + unsupported}</code> "
                        f"(Unsupported: <code>{unsupported}</code>)\nErrors: <code>{errors}</code>"
                    )
                    break

                batch_ids = list(range(current_msg_id, max(current_msg_id - 100, 0), -1))
                messages = await bot.get_messages(chat_id=chat, message_ids=batch_ids)

                if not messages:
                    break

                for message in messages:
                    current_msg_id = message.message_id - 1
                    if temp.CANCEL:
                        break

                    if message.empty:
                        deleted += 1
                        continue
                    elif not message.media:
                        no_media += 1
                        continue
                    elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                        unsupported += 1
                        continue

                    media = getattr(message, message.media.value, None)
                    if not media:
                        unsupported += 1
                        continue

                    media.file_type = message.media.value
                    media.caption = message.caption

                    saved, status = await save_file(media)
                    if saved:
                        total_files += 1
                    elif status == 0:
                        duplicate += 1
                    elif status == 2:
                        errors += 1

                processed = total_files + duplicate + errors + deleted + no_media + unsupported
                if processed % 20 == 0:
                    await msg.edit_text(
                        f"Processed: <code>{processed}</code>\nSaved: <code>{total_files}</code>\nDuplicates: <code>{duplicate}</code>\n"
                        f"Deleted: <code>{deleted}</code>\nNo Media: <code>{no_media + unsupported}</code> (Unsupported: <code>{unsupported}</code>)\n"
                        f"Errors: <code>{errors}</code>",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='index_cancel')]])
                    )

        except Exception as e:
            logger.exception(e)
            await msg.edit(f'Error: {e}')
        else:
            await msg.edit(
                f'Successfully indexed!\n\nSaved: <code>{total_files}</code>\nDuplicates: <code>{duplicate}</code>\n'
                f'Deleted: <code>{deleted}</code>\nNo Media: <code>{no_media + unsupported}</code> (Unsupported: <code>{unsupported}</code>)\nErrors: <code>{errors}</code>'
            )
