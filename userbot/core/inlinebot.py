import json
import os
import re
import time
from uuid import uuid4

from telethon import Button, types
from telethon.events import CallbackQuery, InlineQuery
from youtubesearchpython import VideosSearch

from userbot import catub

from ..assistant.iytdl import (
    download_button,
    get_yt_video_id,
    get_ytthumb,
    result_formatter,
    ytsearch_data,
)
from ..Config import Config
from ..helpers.functions import rand_key
from . import check_owner
from .logger import logging

LOGS = logging.getLogger(__name__)

CAT_IMG = Config.ALIVE_PIC or None
BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\<buttonurl:(?:/{0,2})(.+?)(:same)?\>)")
CATLOGO = "https://telegra.ph/file/493268c1f5ebedc967eba.jpg"


def ibuild_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(Button.url(btn[0], btn[1]))
        else:
            keyb.append([Button.url(btn[0], btn[1])])
    return keyb


@catub.tgbot.on(InlineQuery)
async def inline_handler(event):  # sourcery no-metrics
    builder = event.builder
    result = None
    results = []
    query = event.text
    string = query.lower()
    query.split(" ", 2)
    str_y = query.split(" ", 1)
    string.split()
    query_user_id = event.query.user_id
    if query_user_id == Config.OWNER_ID or query_user_id in Config.SUDO_USERS:
        hmm = re.compile("secret (.*) (.*)")
        match = re.findall(hmm, query)
        if query.startswith("**Catuserbot"):
            buttons = [
                (
                    Button.inline("Stats", data="stats"),
                    Button.url("Repo", "https://github.com/sandy1709/catuserbot"),
                )
            ]
            if CAT_IMG and CAT_IMG.endswith((".jpg", ".png")):
                result = builder.photo(
                    CAT_IMG,
                    # title="Alive cat",
                    text=query,
                    buttons=buttons,
                )
            elif CAT_IMG:
                result = builder.document(
                    CAT_IMG,
                    title="Alive cat",
                    text=query,
                    buttons=buttons,
                )
            else:
                result = builder.article(
                    title="Alive cat",
                    text=query,
                    buttons=buttons,
                )
            await event.answer([result] if result else None)
        elif query.startswith("Inline buttons"):
            markdown_note = query[14:]
            prev = 0
            note_data = ""
            buttons = []
            for match in BTN_URL_REGEX.finditer(markdown_note):
                n_escapes = 0
                to_check = match.start(1) - 1
                while to_check > 0 and markdown_note[to_check] == "\\":
                    n_escapes += 1
                    to_check -= 1
                if n_escapes % 2 == 0:
                    buttons.append(
                        (match.group(2), match.group(3), bool(match.group(4)))
                    )
                    note_data += markdown_note[prev : match.start(1)]
                    prev = match.end(1)
                elif n_escapes % 2 == 1:
                    note_data += markdown_note[prev:to_check]
                    prev = match.start(1) - 1
                else:
                    break
            else:
                note_data += markdown_note[prev:]
            message_text = note_data.strip()
            tl_ib_buttons = ibuild_keyboard(buttons)
            result = builder.article(
                title="Inline creator",
                text=message_text,
                buttons=tl_ib_buttons,
                link_preview=False,
            )
            await event.answer([result] if result else None)
        elif match:
            query = query[7:]
            user, txct = query.split(" ", 1)
            builder = event.builder
            secret = os.path.join("./userbot", "secrets.txt")
            try:
                jsondata = json.load(open(secret))
            except Exception:
                jsondata = False
            try:
                # if u is user id
                u = int(user)
                try:
                    u = await event.client.get_entity(u)
                    if u.username:
                        sandy = f"@{u.username}"
                    else:
                        sandy = f"[{u.first_name}](tg://user?id={u.id})"
                except ValueError:
                    # ValueError: Could not find the input entity
                    sandy = f"[user](tg://user?id={u})"
            except ValueError:
                # if u is username
                try:
                    u = await event.client.get_entity(user)
                except ValueError:
                    return
                if u.username:
                    sandy = f"@{u.username}"
                else:
                    sandy = f"[{u.first_name}](tg://user?id={u.id})"
                u = int(u.id)
            except Exception:
                return
            timestamp = int(time.time() * 2)
            newsecret = {str(timestamp): {"userid": u, "text": txct}}

            buttons = [Button.inline("show message 🔐", data=f"secret_{timestamp}")]
            result = builder.article(
                title="secret message",
                text=f"🔒 A whisper message to {sandy}, Only he/she can open it.",
                buttons=buttons,
            )
            await event.answer([result] if result else None)
            if jsondata:
                jsondata.update(newsecret)
                json.dump(jsondata, open(secret, "w"))
            else:
                json.dump(newsecret, open(secret, "w"))
        if str_y[0].lower() == "ytdl" and len(str_y) == 2:
            link = get_yt_video_id(str_y[1].strip())
            found_ = True
            if link is None:
                search = VideosSearch(str_y[1].strip(), limit=15)
                resp = (search.result()).get("result")
                if len(resp) == 0:
                    found_ = False
                else:
                    outdata = await result_formatter(resp)
                    key_ = rand_key()
                    ytsearch_data.store_(key_, outdata)
                    buttons = [
                        (
                            Button.inline(
                                f"1 / {len(outdata)}",
                                data=f"ytdl_next_{key_}_1",
                            )
                        ),
                        (
                            Button.inline(
                                "📜  List all",
                                data=f"ytdl_listall_{key_}_1",
                            ),
                            Button.inline(
                                "⬇️  Download",
                                data=f'ytdl_download_{outdata[1]["video_id"]}_0',
                            ),
                        ),
                    ]
                    caption = outdata[1]["message"]
                    photo = outdata[1]["thumb"]
            else:
                caption, buttons = await download_button(link, body=True)
                photo = await get_ytthumb(link)
            if found_:
                results.append(
                    builder.photo(
                        photo,
                        # title=link,
                        # description="⬇️ Click to Download",
                        text=caption,
                        buttons=buttons,
                    )
                )
            else:
                results.append(
                    builder.article(
                        title="Not Found",
                        text=f"No Results found for `{str_y[1]}`",
                        description="INVALID",
                    )
                )
            await event.answer(results)
    else:
        buttons = [
            (
                Button.url("Source code", "https://github.com/sandy1709/catuserbot"),
                Button.url(
                    "Deploy",
                    "https://dashboard.heroku.com/new?button-url=https%3A%2F%2Fgithub.com%2FMr-confused%2Fcatpack&template=https%3A%2F%2Fgithub.com%2FMr-confused%2Fcatpack",
                ),
            )
        ]
        markup = event.client.build_reply_markup(buttons)
        photo = types.InputWebDocument(
            url=CATLOGO, size=0, mime_type="image/jpeg", attributes=[]
        )
        text, msg_entities = await event.client._parse_message_text(
            "𝗗𝗲𝗽𝗹𝗼𝘆 𝘆𝗼𝘂𝗿 𝗼𝘄𝗻 𝗖𝗮𝘁𝗨𝘀𝗲𝗿𝗯𝗼𝘁.", "md"
        )
        result = types.InputBotInlineResult(
            id=str(uuid4()),
            type="photo",
            title="𝘾𝙖𝙩𝙐𝙨𝙚𝙧𝙗𝙤𝙩",
            description="Deploy yourself",
            url="https://github.com/sandy1709/catuserbot",
            thumb=photo,
            content=photo,
            send_message=types.InputBotInlineMessageMediaAuto(
                reply_markup=markup, message=text, entities=msg_entities
            ),
        )
        await event.answer([result] if result else None)


@catub.tgbot.on(CallbackQuery(data=re.compile(b"close")))
@check_owner
async def on_plug_in_callback_query_handler(event):
    await event.edit("menu closed")
