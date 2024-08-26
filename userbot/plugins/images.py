# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import contextlib
import os
import shutil

from telethon.errors.rpcerrorlist import ImageProcessFailedError, MediaEmptyError

from userbot import Config, catub

from ..core.logger import logging
from ..core.managers import edit_or_reply
from ..helpers.google_image_download import google_crawl_images, search_and_download_images
from ..helpers.utils import reply_id
from . import BOTLOG_CHATID

LOGS = logging.getLogger("CatUserbot")
plugin_category = "misc"


@catub.cat_cmd(
    pattern=r"img(?: |$)(\d*)? ?([\s\S]*)",
    command=("img", plugin_category),
    info={
        "header": "Google image search.",
        "description": "To search images in google. By default will send 3 images.you can get more images(upto 10 only by changing limit value as shown in usage and examples.",
        "usage": ["{tr}img <1-10> <query>", "{tr}img <query>"],
        "examples": [
            "{tr}img 10 catuserbot",
            "{tr}img catuserbot",
            "{tr}img 7 catuserbot",
        ],
    },
)
async def img_func(event):
    "Google image search."
    reply_to_id = await reply_id(event)
    if event.is_reply and not event.pattern_match.group(2):
        query = await event.get_reply_message()
        query = str(query.message)
    else:
        query = str(event.pattern_match.group(2))
    if not query:
        return await edit_or_reply(event, "Reply to a message or pass a query to search!")
    cat = await edit_or_reply(event, "`Processing...`")
    if event.pattern_match.group(1) != "":
        lim = int(event.pattern_match.group(1))
        lim = min(lim, 10)
        if lim <= 0:
            lim = 1
    else:
        lim = 3

    # passing the arguments to the function
    try:
        downloaded_data = google_crawl_images(query, lim)
    except Exception as e:
        return await cat.edit(f"Error: \n`{e}`")

    try:
        await event.client.send_file(event.chat_id, downloaded_data, reply_to=reply_to_id)
    except (MediaEmptyError, ImageProcessFailedError):
        for i in downloaded_data:
            with contextlib.suppress(MediaEmptyError, ImageProcessFailedError):
                await event.client.send_file(event.chat_id, i, reply_to=reply_to_id)
    except TypeError as e:
        return await cat.edit(f"Error: \n`{e}`")

    shutil.rmtree(os.path.dirname(os.path.abspath(downloaded_data[0])))

    await cat.delete()


@catub.cat_cmd(
    pattern=r"img_api(?: |$)(\d*)? ?([\s\S]*)",
    command=("img_api", plugin_category),
    info={
        "header": "Google image search.",
        "description": "To search images in google. By default will send 3 images.you can get more images(upto 10 only by changing limit value as shown in usage and examples.",
        "usage": ["{tr}img_api <1-10> <query>", "{tr}img_api <query>"],
        "examples": [
            "{tr}img_api 10 catuserbot",
            "{tr}img_api catuserbot",
            "{tr}img_api 7 catuserbot",
        ],
    },
)
async def img_api_func(event):
    "Google image search."
    reply_to_id = await reply_id(event)
    if event.is_reply and not event.pattern_match.group(2):
        query = await event.get_reply_message()
        query = str(query.message)
    else:
        query = str(event.pattern_match.group(2))
    if not query:
        return await edit_or_reply(event, "Reply to a message or pass a query to search!")
    cat = await edit_or_reply(event, "`Processing...`")
    if event.pattern_match.group(1) != "":
        lim = int(event.pattern_match.group(1))
        lim = min(lim, 10)
        if lim <= 0:
            lim = 1
    else:
        lim = 3

    # passing the arguments to the function
    try:
        downloaded_data = search_and_download_images(query, Config.GOOGLE_CONSOLE_API_KEY, Config.GOOGLE_CSE_ID, lim)
    except Exception as e:
        return await cat.edit(f"Error: \n`{e}`")

    lst = downloaded_data["download_path"]

    try:
        await event.client.send_file(event.chat_id, lst, reply_to=reply_to_id)
    except (MediaEmptyError, ImageProcessFailedError):
        for i in lst:
            with contextlib.suppress(MediaEmptyError, ImageProcessFailedError):
                await event.client.send_file(event.chat_id, i, reply_to=reply_to_id)
    except TypeError as e:
        print(lst)
        return await cat.edit(f"Error: \n`{e}`")

    shutil.rmtree(os.path.dirname(os.path.abspath(lst[0])))
    if len(downloaded_data["errors"]) > 0:
        LOGS.error(downloaded_data)
        await catub.send_message(
            BOTLOG_CHATID,
            f"**Error:** while fetching images\n`{', '.join(downloaded_data["errors"])}`",
        )

    await cat.delete()
