# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import contextlib
import html
import os

from requests import get
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest

from userbot import catub
from userbot.core.logger import logging

from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import get_user_from_event, reply_id
from . import spamwatch

plugin_category = "utils"
LOGS = logging.getLogger(__name__)


async def fetch_info(replied_user, event):
    """Get details from the User object."""
    FullUser = (await event.client(GetFullUserRequest(replied_user.id))).full_user
    replied_user_profile_photos = await event.client(GetUserPhotosRequest(user_id=replied_user.id, offset=42, max_id=0, limit=80))
    replied_user_profile_photos_count = "User haven't set profile pic"
    dc_id = "Can't get dc id"
    with contextlib.suppress(AttributeError):
        replied_user_profile_photos_count = replied_user_profile_photos.count
        dc_id = replied_user.photo.dc_id
    user_id = replied_user.id
    first_name = replied_user.first_name
    full_name = FullUser.private_forward_name
    common_chat = FullUser.common_chats_count
    username = replied_user.username
    user_bio = FullUser.about
    is_bot = replied_user.bot
    restricted = replied_user.restricted
    verified = replied_user.verified
    is_premium = (await event.client.get_entity(user_id)).premium
    photo = await event.client.download_profile_photo(
        user_id,
        Config.TMP_DOWNLOAD_DIRECTORY + str(user_id) + ".jpg",
        download_big=True,
    )
    first_name = first_name.replace("\u2060", "") if first_name else ("This User has no First Name")
    full_name = full_name or first_name
    username = f"@{username}" if username else "This User has no Username"
    user_bio = user_bio or "This User has no About"
    caption = "<b><i>USER INFO from Durov's Database :</i></b>\n\n"
    caption += f"<b>👤 Name:</b> {full_name}\n"
    caption += f"<b>🤵 Username:</b> {username}\n"
    caption += f"<b>🔖 ID:</b> <code>{user_id}</code>\n"
    caption += f"<b>🌏 Data Centre ID:</b> {dc_id}\n"
    caption += f"<b>🖼 Number of Profile Pics:</b> {replied_user_profile_photos_count}\n"
    caption += f"<b>⭐️ Is Premium:</b> {is_premium}\n"
    caption += f"<b>🤖 Is Bot:</b> {is_bot}\n"
    caption += f"<b>🔏 Is Restricted:</b> {restricted}\n"
    caption += f"<b>🌐 Is Verified by Telegram:</b> {verified}\n\n"
    caption += f"<b>✍️ Bio:</b> \n<code>{user_bio}</code>\n\n"
    caption += f"<b>👥 Common Chats with this user:</b> {common_chat}\n"
    caption += "<b>🔗 Permanent Link To Profile:</b> "
    caption += f'<a href="tg://user?id={user_id}">{first_name}</a>'
    return photo, caption


@catub.cat_cmd(
    pattern=r"userinfo(?:\s|$)([\s\S]*)",
    command=("userinfo", plugin_category),
    info={
        "header": "Gets information of an user such as restrictions ban by spamwatch or cas.",
        "description": "That is like whether he banned is spamwatch or cas and small info like groups in common, dc ..etc.",
        "usage": "{tr}userinfo <username/userid/reply>",
    },
)
async def _(event):
    "Gets information of an user such as restrictions ban by spamwatch or cas"
    replied_user, reason = await get_user_from_event(event)
    if not replied_user:
        return
    catevent = await edit_or_reply(event, "`Fetching userinfo wait....`")
    FullUser = (await event.client(GetFullUserRequest(replied_user.id))).full_user
    user_id = replied_user.id
    # some people have weird HTML in their names
    first_name = html.escape(replied_user.first_name)
    # https://stackoverflow.com/a/5072031/4723940
    # some Deleted Accounts do not have first_name
    if first_name is not None:
        # some weird people (like me) have more than 4096 characters in their
        # names
        first_name = first_name.replace("\u2060", "")
    # inspired by https://telegram.dog/afsaI181
    common_chats = FullUser.common_chats_count
    try:
        dc_id = replied_user.photo.dc_id
    except AttributeError:
        dc_id = "Can't get dc id"
    if spamwatch:
        if ban := spamwatch.get_ban(user_id):
            sw = f"**Spamwatch Banned :** `True` \n       **-**🤷‍♂️**Reason : **`{ban.reason}`"
        else:
            sw = "**Spamwatch Banned :** `False`"
    else:
        sw = "**Spamwatch Banned :**`Not Connected`"
    try:
        casurl = f"https://api.cas.chat/check?user_id={user_id}"
        data = get(casurl).json()
    except Exception as e:
        LOGS.info(e)
        data = None
    if data:
        if data["ok"]:
            cas = "**Antispam(CAS) Banned :** `True`"
        else:
            cas = "**Antispam(CAS) Banned :** `False`"
    else:
        cas = "**Antispam(CAS) Banned :** `Couldn't Fetch`"
    caption = """**Info of [{}](tg://user?id={}):
   -🔖ID : **`{}`
   **-**👥**Groups in Common : **`{}`
   **-**🌏**Data Centre Number : **`{}`
   **-**🔏**Restricted by telegram : **`{}`
   **-**🦅{}
   **-**👮‍♂️{}
""".format(
        first_name,
        user_id,
        user_id,
        common_chats,
        dc_id,
        replied_user.restricted,
        sw,
        cas,
    )
    await edit_or_reply(catevent, caption)


@catub.cat_cmd(
    pattern=r"whois(?:\s|$)([\s\S]*)",
    command=("whois", plugin_category),
    info={
        "header": "Gets info of an user.",
        "description": "User compelete details.",
        "usage": "{tr}whois <username/userid/reply>",
    },
)
async def who(event):
    "Gets info of an user"
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    replied_user, reason = await get_user_from_event(event)
    if not replied_user:
        return
    cat = await edit_or_reply(event, "`Fetching userinfo wait....`")
    try:
        photo, caption = await fetch_info(replied_user, event)
    except (AttributeError, TypeError):
        return await edit_delete(cat, "`Could not fetch info of that user.`")
    message_id_to_reply = await reply_id(event)
    try:
        await event.client.send_file(
            event.chat_id,
            photo,
            caption=caption,
            link_preview=False,
            force_document=False,
            reply_to=message_id_to_reply,
            parse_mode="html",
        )
        if not photo.startswith("http"):
            os.remove(photo)
        await cat.delete()
    except TypeError:
        await cat.edit(caption, parse_mode="html")


@catub.cat_cmd(
    pattern=r"link(?:\s|$)([\s\S]*)",
    command=("link", plugin_category),
    info={
        "header": "Generates a link to the user's PM .",
        "usage": "{tr}link <username/userid/reply>",
    },
)
async def permalink(mention):
    """Generates a link to the user's PM with a custom text."""
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if custom:
        return await edit_or_reply(mention, f"[{custom}](tg://user?id={user.id})")
    tag = user.first_name.replace("\u2060", "") if user.first_name else user.username
    await edit_or_reply(mention, f"[{tag}](tg://user?id={user.id})")
