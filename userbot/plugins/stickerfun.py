# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Special credits:
# @PhycoNinja13b <Telegram> (for Random RGB Sticklet)
# @UniBorg <Telegram> (Modification)
# @heyworld & @DeletedUser420 <Telegram> (imported from ppe-remix)
#
# @SnapDragon7410 <Telegram> (RegEx)
# https://t.me/c/1220993104/500653
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import os
import random
import textwrap
import urllib
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

from userbot import Convert, catub

from ..core.managers import edit_delete, edit_or_reply
from ..helpers.functions import clippy, deEmojify, hide_inlinebot, higlighted_text, soft_deEmojify, waifutxt
from ..helpers.utils import reply_id

plugin_category = "fun"


def file_checker(template):
    if not os.path.isdir("./temp"):
        os.mkdir("./temp")
    tempname = "./temp/cat_temp.png"
    fontname = "./temp/ArialUnicodeMS.ttf"
    urllib.request.urlretrieve(template, tempname)
    if not os.path.exists(fontname):
        urllib.request.urlretrieve(
            "https://github.com/TgCatUB/CatUserbot-Resources/blob/master/Resources/Spotify/ArialUnicodeMS.ttf?raw=true",
            fontname,
        )
    return tempname, fontname


@catub.cat_cmd(
    pattern=r"(?:st|sttxt)(?:\s|$)([\s\S]*)",
    command=("sttxt", plugin_category),
    info={
        "header": "Anime that makes your writing fun.",
        "usage": "{tr}sttxt <text>",
        "examples": "{tr}sttxt hello",
    },
)
async def waifu(animu):
    "Anime that makes your writing fun"
    text = animu.pattern_match.group(1)
    reply_to_id = await reply_id(animu)
    if not text:
        if animu.is_reply:
            text = (await animu.get_reply_message()).message
        else:
            return await edit_or_reply(animu, "`You haven't written any article, Waifu is going away.`")
    text = deEmojify(text)
    await animu.delete()
    await waifutxt(text, animu.chat_id, reply_to_id, animu.client)


@catub.cat_cmd(
    pattern=r"stcr(?:\s|$)([\s\S]*)",
    command=("stcr", plugin_category),
    info={
        "header": "your text as sticker.",
        "usage": "{tr}stcr <text/reply>",
        "examples": "{tr}stcr hello",
    },
)
async def sticklet(event):
    "your text as sticker"
    RGB = tuple(random.sample(range(255), 3))
    reply_to_id = await reply_id(event)
    sticktext = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if not sticktext and reply:
        sticktext = reply.text
    if not sticktext:
        return await edit_delete(event, "`Need text to write..`")
    sticktext = deEmojify(sticktext)
    sticktext = textwrap.wrap(sticktext, width=10)
    # converts back the list to a string
    sticktext = "\n".join(sticktext)
    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230
    json = requests.get("https://raw.githubusercontent.com/TgCatUB/CatUserbot-Resources/master/Resources/StickerFun/resources.txt").json()
    FONT_FILE = requests.get(random.choice(json["fonts"]))
    font = ImageFont.truetype(BytesIO(FONT_FILE.content), size=fontsize)
    while draw.multiline_textsize(sticktext, font=font) > (512, 512):
        fontsize -= 3
        font = ImageFont.truetype(BytesIO(FONT_FILE.content), size=fontsize)
    width, height = draw.multiline_textsize(sticktext, font=font)
    draw.multiline_text(((512 - width) / 2, (512 - height) / 2), sticktext, font=font, fill=(RGB))
    image_stream = BytesIO()
    image_stream.name = "catuserbot.webp"
    image.save(image_stream, "WebP")
    image_stream.seek(0)
    # finally, reply the sticker
    await event.delete()
    await event.client.send_file(
        event.chat_id,
        image_stream,
        reply_to=reply_to_id,
    )


@catub.cat_cmd(
    pattern=r"honk(?:\s|$)([\s\S]*)",
    command=("honk", plugin_category),
    info={
        "header": "Make honk say anything.",
        "usage": "{tr}honk <text/reply to msg>",
        "examples": "{tr}honk How you doing?",
    },
)
async def honk(event):
    "Make honk say anything."
    text = event.pattern_match.group(1)
    reply_to_id = await reply_id(event)
    bot_name = "@honka_says_bot"
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            return await edit_delete(event, "__What is honk supposed to say? Give some text.__")
    text = soft_deEmojify(text)
    await event.delete()
    await hide_inlinebot(event.client, bot_name, text, event.chat_id, reply_to_id)


@catub.cat_cmd(
    pattern=r"twt(?:\s|$)([\s\S]*)",
    command=("twt", plugin_category),
    info={
        "header": "Make a cool tweet of your account",
        "usage": "{tr}twt <text/reply to msg>",
        "examples": "{tr}twt Catuserbot",
    },
)
async def twt(event):
    "Make a cool tweet of your account."
    text = event.pattern_match.group(1)
    reply_to_id = await reply_id(event)
    bot_name = "@TwitterStatusBot"
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            return await edit_delete(event, "__What am I supposed to Tweet? Give some text.__")
    text = soft_deEmojify(text)
    await event.delete()
    await hide_inlinebot(event.client, bot_name, text, event.chat_id, reply_to_id)


@catub.cat_cmd(
    pattern=r"glax(|r)(?:\s|$)([\s\S]*)",
    command=("glax", plugin_category),
    info={
        "header": "Make glax the dragon scream your text.",
        "flags": {
            "r": "Reverse the face of the dragon",
        },
        "usage": [
            "{tr}glax <text/reply to msg>",
            "{tr}glaxr <text/reply to msg>",
        ],
        "examples": [
            "{tr}glax Die you",
            "{tr}glaxr Die you",
        ],
    },
)
async def glax(event):
    "Make glax the dragon scream your text."
    cmd = event.pattern_match.group(1).lower()
    text = event.pattern_match.group(2)
    reply_to_id = await reply_id(event)
    bot_name = "@GlaxScremBot"
    c_lick = 1 if cmd == "r" else 0
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            return await edit_delete(event, "What is glax supposed to scream? Give text..")
    text = soft_deEmojify(text)
    await event.delete()
    await hide_inlinebot(event.client, bot_name, text, event.chat_id, reply_to_id, c_lick=c_lick)


@catub.cat_cmd(
    pattern=r"(|b)quby(?:\s|$)([\s\S]*)",
    command=("quby", plugin_category),
    info={
        "header": "Make doge say anything.",
        "flags": {
            "b": "Give the sticker on background.",
        },
        "usage": [
            "{tr}quby <text/reply to msg>",
            "{tr}bquby <text/reply to msg>",
        ],
        "examples": [
            "{tr}quby Gib money",
            "{tr}bquby Gib money",
        ],
    },
)
async def quby(event):
    "Make a cool quby text sticker"
    cmd = event.pattern_match.group(1).lower()
    text = event.pattern_match.group(2)
    reply_to_id = await reply_id(event)
    if not text and event.is_reply:
        text = (await event.get_reply_message()).message
    if not text:
        return await edit_delete(event, "__What is quby supposed to say? Give some text.__")
    await edit_delete(event, "`Wait, processing.....`")
    temp_name, fontname = file_checker("https://graph.org/file/09f4df5a129758a2e1c9c.jpg")
    lines = 3
    text = soft_deEmojify(text)
    if len(text) < 80:
        font = 60
        wrap = 1.3
        position = (45, 0)
    else:
        font = 50
        wrap = 1
        position = (-70, 0)
    file, txt = higlighted_text(
        temp_name,
        text,
        text_wrap=wrap,
        font_name=fontname,
        font_size=font,
        linespace="+2",
        position=position,
        lines=lines,
        album=True,
        album_limit=1,
        stroke_width=1,
    )
    if len(txt) >= lines:
        for x in range(lines):
            text = text.replace(txt[x], "")
        file, _ = higlighted_text(
            file[0],
            text,
            text_wrap=wrap,
            font_name=fontname,
            font_size=font,
            linespace="+2",
            position=position,
            direction="upwards",
            lines=1,
            album=True,
            album_limit=1,
            stroke_width=1,
        )
    if cmd == "b":
        cat = (await Convert.to_sticker(event, file[0], file="quby.webp", noedits=True))[1]
        await event.client.send_file(event.chat_id, cat, reply_to=reply_to_id, force_document=False)
    else:
        await clippy(event.client, file[0], event.chat_id, reply_to_id)
    await event.delete()
    for files in (temp_name, file[0]):
        if files and os.path.exists(files):
            os.remove(files)


@catub.cat_cmd(
    pattern=r"(|b)(blob|kirby)(?:\s|$)([\s\S]*)",
    command=("blob", plugin_category),
    info={
        "header": "Give the sticker on background.",
        "flags": {
            "b": "To create knife sticker transparent.",
        },
        "usage": [
            "{tr}blob/kirby <text/reply to msg>",
            "{tr}bblob/bkirby <text/reply to msg>",
        ],
        "examples": [
            "{tr}blob Gib money",
            "{tr}bblob Gib money",
        ],
    },
)
async def knife(event):
    "Make a blob knife text sticker"
    cmd = event.pattern_match.group(1).lower()
    text = event.pattern_match.group(3)
    reply_to_id = await reply_id(event)
    if not text and event.is_reply:
        text = (await event.get_reply_message()).message
    if not text:
        return await edit_delete(event, "__What is blob supposed to say? Give some text.__")
    await edit_delete(event, "`Wait, processing.....`")
    temp_name, fontname = file_checker("https://graph.org/file/2188367c8c5f43c36aa59.jpg")
    text = soft_deEmojify(text)
    if len(text) < 50:
        font = 90
        wrap = 2

        position = (250, -450)
    else:
        font = 60
        wrap = 1.4
        position = (150, 500)
    file, _ = higlighted_text(
        temp_name,
        text,
        text_wrap=wrap,
        font_name=fontname,
        font_size=font,
        linespace="-5",
        position=position,
        direction="upwards",
    )
    if cmd == "b":
        cat = (await Convert.to_sticker(event, file[0], file="knife.webp", noedits=True))[1]
        await event.client.send_file(event.chat_id, cat, reply_to=reply_to_id, force_document=False)
    else:
        await clippy(event.client, file[0], event.chat_id, reply_to_id)
    await event.delete()
    for files in (temp_name, file[0]):
        if files and os.path.exists(files):
            os.remove(files)


@catub.cat_cmd(
    pattern=r"doge(?:\s|$)([\s\S]*)",
    command=("doge", plugin_category),
    info={
        "header": "Make doge say anything.",
        "usage": "{tr}doge <text/reply to msg>",
        "examples": "{tr}doge Gib money",
    },
)
async def doge(event):
    "Make a cool doge text sticker"
    text = event.pattern_match.group(1)
    reply_to_id = await reply_id(event)
    if not text and event.is_reply:
        text = (await event.get_reply_message()).message
    if not text:
        return await edit_delete(event, "__What is doge supposed to say? Give some text.__")
    await edit_delete(event, "`Wait, processing.....`")
    text = soft_deEmojify(text)
    temp_name, fontname = file_checker("https://graph.org/file/6f621b9782d9c925bd6c4.jpg")
    font, wrap, lines, ls = (90, 1.9, 5, "-75") if len(text) < 140 else (70, 1.3, 6, "-55")
    file, txt = higlighted_text(
        temp_name,
        text,
        text_wrap=wrap,
        font_name=fontname,
        font_size=font,
        linespace=ls,
        position=(-20, 0),
        align="left",
        background="white",
        foreground="black",
        transparency=0,
        lines=lines,
        album=True,
        album_limit=1,
        stroke_width=1,
        stroke_fill="black",
    )
    if len(txt) >= lines:
        for x in range(lines):
            text = text.replace(txt[x], "")
        file, _ = higlighted_text(
            file[0],
            text,
            text_wrap=wrap + 2,
            font_name=fontname,
            font_size=font,
            linespace=ls,
            position=(-20, 480),
            align="left",
            background="white",
            foreground="black",
            transparency=0,
            lines=lines,
            album=True,
            album_limit=1,
            stroke_width=1,
            stroke_fill="black",
        )
    cat = (await Convert.to_sticker(event, file[0], file="doge.webp", noedits=True))[1]
    await event.client.send_file(event.chat_id, cat, reply_to=reply_to_id, force_document=False)
    await event.delete()
    for files in (temp_name, file[0]):
        if files and os.path.exists(files):
            os.remove(files)


@catub.cat_cmd(
    pattern=r"(|h)penguin(?:\s|$)([\s\S]*)",
    command=("penguin", plugin_category),
    info={
        "header": "To make penguin meme sticker. ",
        "flags": {
            "h": "To create penguin sticker with highligted text.",
        },
        "usage": [
            "{tr}penguin <text/reply to msg>",
            "{tr}hpenguin <text/reply to msg>",
        ],
        "examples": [
            "{tr}penguin Shut up Rash",
            "{tr}hpenguin Shut up Rash",
        ],
    },
)
async def penguin(event):
    "Make a cool penguin text sticker"
    cmd = event.pattern_match.group(1).lower()
    text = event.pattern_match.group(2)
    reply_to_id = await reply_id(event)
    if not text and event.is_reply:
        text = (await event.get_reply_message()).message
    if not text:
        return await edit_delete(event, "What is penguin supposed to say? Give some text.")
    await edit_delete(event, "Wait, processing.....")
    temp_name, fontname = file_checker("https://graph.org/file/ee1fc91bbaef2cc808c7c.png")
    text = soft_deEmojify(text)
    font, wrap, lines = (90, 4, 5) if len(text) < 50 else (70, 4.5, 7)
    bg, fg, alpha, ls, lines = ("black", "white", 255, "-30", lines - 2) if cmd == "h" else ("white", "black", 0, "-60", lines)
    file, _ = higlighted_text(
        temp_name,
        text,
        text_wrap=wrap,
        font_name=fontname,
        font_size=font,
        linespace=ls,
        position=(0, 10),
        align="left",
        background=bg,
        foreground=fg,
        transparency=alpha,
        lines=lines,
        album=True,
        album_limit=1,
        stroke_width=1,
        stroke_fill=fg,
    )
    cat = (await Convert.to_sticker(event, file[0], file="penguin.webp", noedits=True))[1]
    await event.client.send_file(event.chat_id, cat, reply_to=reply_to_id, force_document=False)
    await event.delete()
    for files in (temp_name, file[0]):
        if files and os.path.exists(files):
            os.remove(files)


@catub.cat_cmd(
    pattern=r"(|h)gandhi(?:\s|$)([\s\S]*)",
    command=("gandhi", plugin_category),
    info={
        "header": "Make gandhi text sticker.",
        "flags": {
            "h": "To create gandhi sticker with highligted text.",
        },
        "usage": [
            "{tr}gandhi <text/reply to msg>",
            "{tr}hgandhi <text/reply to msg>",
        ],
        "examples": [
            "{tr}gandhi Nathu Killed me",
            "{tr}hgandhi Nathu Killed me",
        ],
    },
)
async def gandhi(event):
    "Make a cool gandhi text sticker"
    cmd = event.pattern_match.group(1).lower()
    text = event.pattern_match.group(2)
    reply_to_id = await reply_id(event)
    if not text and event.is_reply:
        text = (await event.get_reply_message()).message
    if not text:
        return await edit_delete(event, "What is gandhi supposed to write? Give some text.")
    await edit_delete(event, "Wait, processing.....")
    temp_name, fontname = file_checker("https://graph.org/file/3bebc56ee82cce4f300ce.jpg")
    text = soft_deEmojify(text)
    font, wrap, lines = (90, 3, 5) if len(text) < 75 else (70, 2.8, 7)
    bg, fg, alpha, ls, lines = ("white", "black", 255, "-30", lines - 1) if cmd == "h" else ("black", "white", 0, "-60", lines)
    file, _ = higlighted_text(
        temp_name,
        text,
        text_wrap=wrap,
        font_name=fontname,
        font_size=font,
        linespace=ls,
        position=(470, 10),
        align="center",
        background=bg,
        foreground=fg,
        transparency=alpha,
        lines=lines,
        album=True,
        album_limit=1,
        stroke_width=1,
        stroke_fill=fg,
    )
    cat = (await Convert.to_sticker(event, file[0], file="gandhi.webp", noedits=True))[1]
    await event.client.send_file(event.chat_id, cat, reply_to=reply_to_id, force_document=False)
    await event.delete()
    for files in (temp_name, file[0]):
        if files and os.path.exists(files):
            os.remove(files)
