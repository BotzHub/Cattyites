# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import asyncio
import glob
import io
import os
import pathlib
from time import time

from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl import types
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.utils import get_attributes
from urlextract import URLExtract
from wget import download
from yt_dlp import YoutubeDL
from yt_dlp.utils import ContentTooShortError, DownloadError, ExtractorError, GeoRestrictedError, MaxDownloadsReached, PostProcessingError, UnavailableVideoError, XAttrMetadataError

from ..Config import Config
from ..core import pool
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import progress, reply_id
from ..helpers.functions import delete_conv
from ..helpers.functions.utube import _mp3Dl, get_yt_video_id, get_ytthumb, ytsearch
from ..helpers.utils import _format
from . import catub

BASE_YT_URL = "https://www.youtube.com/watch?v="
extractor = URLExtract()
LOGS = logging.getLogger(__name__)

plugin_category = "misc"


video_opts = {
    "format": "best",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "writethumbnail": True,
    "prefer_ffmpeg": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [
        {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
        {"key": "FFmpegMetadata"},
    ],
    "outtmpl": "cat_ytv.mp4",
    "logtostderr": False,
    "quiet": True,
}


async def ytdl_down(event, opts, url):
    ytdl_data = None
    try:
        await event.edit("`Fetching data, please wait..`")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await event.edit(f"`{DE}`")
    except ContentTooShortError:
        await event.edit("`The download content was too short.`")
    except GeoRestrictedError:
        await event.edit("`Video is not available from your geographic location due to geographic restrictions imposed by a website.`")
    except MaxDownloadsReached:
        await event.edit("`Max-downloads limit has been reached.`")
    except PostProcessingError:
        await event.edit("`There was an error during post processing.`")
    except UnavailableVideoError:
        await event.edit("`Media is not available in the requested format.`")
    except XAttrMetadataError as XAME:
        await event.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
    except ExtractorError:
        await event.edit("`There was an error during info extraction.`")
    except Exception as e:
        await event.edit(f"**Error : **\n__{e}__")
    return ytdl_data


async def fix_attributes(path, info_dict: dict, supports_streaming: bool = False, round_message: bool = False) -> list:
    """Avoid multiple instances of an attribute."""
    new_attributes = []
    video = False
    audio = False

    uploader = info_dict.get("uploader", "Unknown artist")
    duration = int(info_dict.get("duration", 0))
    suffix = path.suffix[1:]
    if supports_streaming and suffix != "mp4":
        supports_streaming = True

    attributes, mime_type = get_attributes(path)
    if suffix == "mp3":
        title = str(info_dict.get("title", info_dict.get("id", "Unknown title")))
        audio = types.DocumentAttributeAudio(duration=duration, voice=None, title=title, performer=uploader)
    elif suffix == "mp4":
        width = int(info_dict.get("width", 0))
        height = int(info_dict.get("height", 0))
        for attr in attributes:
            if isinstance(attr, types.DocumentAttributeVideo):
                duration = duration or attr.duration
                width = width or attr.w
                height = height or attr.h
                break
        video = types.DocumentAttributeVideo(
            duration=duration,
            w=width,
            h=height,
            round_message=round_message,
            supports_streaming=supports_streaming,
        )

    if audio and isinstance(audio, types.DocumentAttributeAudio):
        new_attributes.append(audio)
    if video and isinstance(video, types.DocumentAttributeVideo):
        new_attributes.append(video)

    new_attributes.extend(
        attr
        for attr in attributes
        if (isinstance(attr, types.DocumentAttributeAudio) and not audio or not isinstance(attr, types.DocumentAttributeAudio) and not video or not isinstance(attr, types.DocumentAttributeAudio) and not isinstance(attr, types.DocumentAttributeVideo))
    )
    return new_attributes, mime_type


@catub.cat_cmd(
    pattern=r"yta(?:\s|$)([\s\S]*)",
    command=("yta", plugin_category),
    info={
        "header": "To download audio from many sites like Youtube, Facebook, Instagram, etc.",
        "description": "downloads the audio from the given link ([Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md))",
        "examples": ["{tr}yta <reply to link>", "{tr}yta <link>"],
    },
)
async def download_audio(event):  # sourcery skip: low-code-quality
    """To download audio from YouTube and many other sites."""
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "What I am Supposed to do? Give link")
    catevent = await edit_or_reply(event, "`Preparing to download...`")
    reply_to_id = await reply_id(event)
    for url in urls:
        try:
            vid_data = YoutubeDL({"no-playlist": True}).extract_info(url, download=False)
        except ExtractorError:
            vid_data = {"title": url, "uploader": "Catuserbot", "formats": []}
        startTime = time()
        retcode = await _mp3Dl(url=url, starttime=startTime, uid="320")
        if retcode != 0:
            return await event.edit(str(retcode))
        _fpath = ""
        thumb_pic = None
        for _path in glob.glob(os.path.join(Config.TEMP_DIR, str(startTime), "*")):
            if _path.lower().endswith((".jpg", ".png", ".webp")):
                thumb_pic = _path
            else:
                _fpath = _path
        if not _fpath:
            return await edit_delete(catevent, "__Unable to upload file__")
        await catevent.edit(
            f"`Preparing to upload video:`\
            \n**{vid_data['title']}***"
        )
        attributes, mime_type = get_attributes(str(_fpath))
        ul = io.open(pathlib.Path(_fpath), "rb")
        if thumb_pic is None:
            thumb_pic = str(await pool.run_in_thread(download)(await get_ytthumb(get_yt_video_id(url))))
        uploaded = await event.client.fast_upload_file(
            file=ul,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    catevent,
                    startTime,
                    "trying to upload",
                    file_name=os.path.basename(pathlib.Path(_fpath)),
                )
            ),
        )
        ul.close()
        media = types.InputMediaUploadedDocument(
            file=uploaded,
            mime_type=mime_type,
            attributes=attributes,
            force_file=False,
            thumb=await event.client.upload_file(thumb_pic) if thumb_pic else None,
        )
        await event.client.send_file(
            event.chat_id,
            file=media,
            caption=f"<b>File Name : </b><code>{vid_data.get('title', os.path.basename(pathlib.Path(_fpath)))}</code>",
            supports_streaming=True,
            reply_to=reply_to_id,
            parse_mode="html",
        )
        for _path in [_fpath, thumb_pic]:
            os.remove(_path)
    await catevent.delete()


@catub.cat_cmd(
    pattern=r"ytv(?:\s|$)([\s\S]*)",
    command=("ytv", plugin_category),
    info={
        "header": "To download video from many sites like Youtube, Facebook, Instagram",
        "description": "downloads the video from the given link ([Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md))",
        "examples": [
            "{tr}ytv <reply to link>",
            "{tr}ytv <link>",
        ],
    },
)
async def download_video(event):
    """To download video from YouTube and many other sites."""
    msg = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "What I am Supposed to do? Give link")
    catevent = await edit_or_reply(event, "`Preparing to download...`")
    reply_to_id = await reply_id(event)
    for url in urls:
        ytdl_data = await ytdl_down(catevent, video_opts, url)
        if ytdl_down is None:
            return
        try:
            f = pathlib.Path("cat_ytv.mp4")
            catthumb = pathlib.Path("cat_ytv.jpg")
            if not os.path.exists(catthumb):
                catthumb = pathlib.Path("cat_ytv.webp")
            if not os.path.exists(catthumb):
                catthumb = None
            await catevent.edit(
                f"`Preparing to upload video:`\
                \n**{ytdl_data['title']}**"
            )
            ul = io.open(f, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(f, ytdl_data, supports_streaming=True)
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(progress(d, t, catevent, c_time, "Upload :", file_name=ytdl_data["title"])),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
            )
            await event.client.send_file(
                event.chat_id,
                file=media,
                reply_to=reply_to_id,
                caption=f'**Title :** `{ytdl_data["title"]}`',
                thumb=catthumb,
            )
            os.remove(f)
            if catthumb:
                os.remove(catthumb)
        except TypeError:
            await asyncio.sleep(2)
    await event.delete()


@catub.cat_cmd(
    pattern=r"insta(?: |$)([\s\S]*)",
    command=("insta", plugin_category),
    info={
        "header": "To download instagram video/photo",
        "description": "Note downloads only public profile photos/videos.",
        "examples": [
            "{tr}insta <link>",
        ],
    },
)
async def insta_dl(event):
    "For downloading instagram media"
    link = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if not link and reply:
        link = reply.text
    if not link:
        return await edit_delete(event, "**ಠ∀ಠ Give me link to search..**", 10)
    if "instagram.com" not in link:
        return await edit_delete(event, "` I need a Instagram link to download it's Video...`(*_*)", 10)
    # v1 = "@instasave_bot"
    # v1 = "@IgGramBot"
    v1 = "Fullsavebot"
    v2 = "@videomaniacbot"
    media_list = []
    catevent = await edit_or_reply(event, "**Downloading.....**")
    async with event.client.conversation(v1) as conv:
        try:
            v1_flag = await conv.send_message("/start")
        except YouBlockedUserError:
            await catub(unblock("Fullsavebot"))
            v1_flag = await conv.send_message("/start")
        checker = await conv.get_response()
        await event.client.send_read_acknowledge(conv.chat_id)
        if "Choose the language you like" in checker.message:
            await checker.click(1)
            await conv.send_message(link)
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
        await conv.send_message(link)
        await conv.get_response()
        await event.client.send_read_acknowledge(conv.chat_id)
        try:
            media = await conv.get_response(timeout=10)
            await event.client.send_read_acknowledge(conv.chat_id)
            if media.media:
                while True:
                    media_list.append(media)
                    try:
                        media = await conv.get_response(timeout=2)
                        await event.client.send_read_acknowledge(conv.chat_id)
                    except asyncio.TimeoutError:
                        break
                details = media_list[0].message.splitlines()
                await catevent.delete()
                await event.client.send_file(
                    event.chat_id,
                    media_list,
                    caption=f"**{details[0]}**",
                )
                return await delete_conv(event, v1, v1_flag)
        except asyncio.TimeoutError:
            await delete_conv(event, v1, v1_flag)
        await edit_or_reply(catevent, "**Switching v2...**")
        async with event.client.conversation(v2) as conv:
            try:
                v2_flag = await conv.send_message("/start")
            except YouBlockedUserError:
                await catub(unblock("videomaniacbot"))
                v2_flag = await conv.send_message("/start")
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            await asyncio.sleep(1)
            await conv.send_message(link)
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            media = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            if media.media:
                await catevent.delete()
                await event.client.send_file(event.chat_id, media)
            else:
                await edit_delete(
                    catevent,
                    f"**#ERROR\nv1 :** __Not valid URL__\n\n**v2 :**__ {media.text}__",
                    40,
                )
            await delete_conv(event, v2, v2_flag)


@catub.cat_cmd(
    pattern=r"yts(?: |$)(\d*)? ?([\s\S]*)",
    command=("yts", plugin_category),
    info={
        "header": "To search youtube videos",
        "description": "Fetches youtube search results with views and duration with required no of count results by default it fetches 10 results",
        "examples": [
            "{tr}yts <query>",
            "{tr}yts <1-9> <query>",
        ],
    },
)
async def yt_search(event):
    "Youtube search command"
    if event.is_reply and not event.pattern_match.group(2):
        query = await event.get_reply_message()
        query = str(query.message)
    else:
        query = str(event.pattern_match.group(2))
    if not query:
        return await edit_delete(event, "`Reply to a message or pass a query to search!`")
    video_q = await edit_or_reply(event, "`Searching...`")
    if event.pattern_match.group(1) != "":
        lim = int(event.pattern_match.group(1))
        if lim <= 0:
            lim = 10
    else:
        lim = 10
    try:
        full_response = await ytsearch(query, limit=lim)
    except Exception as e:
        return await edit_delete(video_q, str(e), time=10, parse_mode=_format.parse_pre)
    reply_text = f"**•  Search Query:**\n`{query}`\n\n**•  Results:**\n{full_response}"
    await edit_or_reply(video_q, reply_text)
