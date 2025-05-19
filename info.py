import re
from os import environ

id_pattern = re.compile(r'^-?\d+$')

def is_enabled(value, default):
    if value is None:
        return default
    value = value.lower()
    if value in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID', '0'))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', '')

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled(environ.get('USE_CAPTION_FILTER'), False)
PICS = environ.get('PICS', 'https://ibb.co/Z1xNkYQm').split()

# Admins, Channels & Users
ADMINS = [int(admin) for admin in environ.get('ADMINS', '').split() if admin and id_pattern.match(admin)]
CHANNELS = [int(ch) for ch in environ.get('CHANNELS', '').split() if ch and id_pattern.match(ch)]
auth_users = [int(user) for user in environ.get('AUTH_USERS', '').split() if user and id_pattern.match(user)]
AUTH_USERS = (auth_users + ADMINS) if auth_users else ADMINS

AUTH_CHANNEL = int(environ.get('AUTH_CHANNEL', '0'))
auth_grp = environ.get('AUTH_GROUP')
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp and auth_grp.strip() else []

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "Anurag")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Anurag_files')

# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '0'))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'MOVIES_ZILAA')
P_TTI_SHOW_OFF = is_enabled(environ.get('P_TTI_SHOW_OFF'), False)
IMDB = is_enabled(environ.get('IMDB'), True)
SINGLE_BUTTON = is_enabled(environ.get('SINGLE_BUTTON'), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "<b><i>{file_name} » {file_size} › [ᎯℕUℛᎯᎶ](https://t.me/MOVIES_ZILAA)</i></b>")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", "🏷 𝖳𝗂𝗍𝗅𝖾: <a href={url}>{title}</a> \n🔮 𝖸𝖾𝖺𝗋: {year} \n⭐️ 𝖱𝖺𝗍𝗂𝗇𝗀𝗌: {rating}/ 10 \n🎭 𝖦𝖾𝗇𝖾𝗋𝗌: {genres} \n\n🎊 𝖯𝗈𝗐𝖾𝗋𝖾𝖽 𝖡𝗒 [ᴀᴍ_ᴛᴇᴄʜ](https://t.me/Am_RoBots)")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in environ.get('FILE_STORE_CHANNEL', '').split() if ch and id_pattern.match(ch)]
MELCOW_NEW_USERS = is_enabled(environ.get('MELCOW_NEW_USERS'), True)
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT'), False)
PUBLIC_FILE_STORE = is_enabled(environ.get('PUBLIC_FILE_STORE'), True)

LOG_STR = "Current Customized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for your queries.\n" if IMDB else "IMDB Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found, users will be redirected to send /start to Bot PM instead of sending file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled, files will be sent in PM instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is enabled, filename and file size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled, filename and file size will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be sent along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION found, default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled.\n" if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled, plot will be shorter.\n")
LOG_STR += ("Spell Check Mode is enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full list of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"
