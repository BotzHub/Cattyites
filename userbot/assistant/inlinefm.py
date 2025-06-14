# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# Special Credit: MineisZarox https://t.me/IrisZarox (Demon)

import asyncio
import io
import os
import time
from pathlib import Path

from telethon import Button, types
from telethon.events import CallbackQuery
from telethon.utils import get_attributes

from userbot import catub
from userbot.Config import Config
from userbot.core.decorators import check_owner
from userbot.helpers import humanbytes, progress
from userbot.helpers.utils import _catutils

CC = []
PATH = []  # using list method for some reason
thumb_image_path = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")


# freaking selector
def add_s(msg, num: int):
    msgs = msg.splitlines()
    leng = len(msgs)
    if num == 0:
        valv = leng - 1
    elif num == leng:
        valv = 1
    else:
        valv = num
    msgs[valv] = f"{msgs[valv]} ⭕️"
    fmsg = "".join(f"{ff}\n" for ff in msgs)
    buttons = [
        [
            Button.inline("D", data=f"fmrem_{msgs[valv]}|{valv}"),
            Button.inline("X", data=f"fmcut_{msgs[valv]}|{valv}"),
            Button.inline("C", data=f"fmcopy_{msgs[valv]}|{valv}"),
            Button.inline("V", data=f"fmpaste_{valv}"),
        ],
        [
            Button.inline("⬅️", data="fmback"),
            Button.inline("⬆️", data=f"fmup_{valv}"),
            Button.inline("⬇️", data=f"fmdown_{valv}"),
            Button.inline("➡️", data=f"fmforth_{msgs[valv]}"),
        ],
    ]
    return fmsg, buttons


def get_manager(path, num: int):
    if os.path.isdir(path):
        return manage_dir(path, num)
    size = os.stat(path).st_size
    msg = "The details of given file :\n"
    if str(path).endswith((".mp3", ".flac", ".wav", ".m4a")):
        mode = "🎧"
    if str(path).endswith((".opus")):
        mode = "🎤"
    elif str(path).endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
        mode = "🎬"
    elif str(path).endswith((".zip", ".tar", ".tar.gz", ".rar")):
        mode = "📚"
    elif str(path).endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")):
        mode = "🏞"
    elif str(path).endswith((".py")):
        mode = "🐍"
    else:
        mode = "📔"
    time.ctime(os.path.getctime(path))
    time2 = time.ctime(os.path.getmtime(path))
    time3 = time.ctime(os.path.getatime(path))
    msg += f"**Location :** `{path}`\n"
    msg += f"**icon :** `{mode}`\n"
    msg += f"**Size :** `{humanbytes(size)}`\n"
    msg += f"**Last Modified Time:** `{time2}`\n"
    msg += f"**Last Accessed Time:** `{time3}`"
    buttons = [
        [
            Button.inline("Rem", data=f"fmrem_File|{num}"),
            Button.inline("Send", data="fmsend"),
            Button.inline("X", data=f"fmcut_File|{num}"),
            Button.inline("C", data=f"fmcopy_File{num}"),
        ],
        [
            Button.inline("⬅️", data="fmback"),
            Button.inline("⬆️", data="fmup_File"),
            Button.inline("⬇️", data="fmdown_File"),
            Button.inline("➡️", data="fmforth_File"),
        ],
    ]
    PATH.clear()
    PATH.append(path)
    return msg, buttons


def manage_dir(path, num):
    msg = f"Folders and Files in `{path}` :\n"
    lists = sorted(os.listdir(path))
    files = ""
    folders = ""
    for contents in sorted(lists):
        zpath = os.path.join(path, contents)
        if not os.path.isdir(zpath):
            if str(contents).endswith((".mp3", ".flac", ".wav", ".m4a")):
                files += f"🎧`{contents}`\n"
            if str(contents).endswith((".opus")):
                files += f"🎤`{contents}`\n"
            elif str(contents).endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
                files += f"🎬`{contents}`\n"
            elif str(contents).endswith((".zip", ".tar", ".tar.gz", ".rar")):
                files += f"📚`{contents}`\n"
            elif str(contents).endswith((".py")):
                files += f"🐍`{contents}`\n"
            elif str(contents).endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")):
                files += f"🏞`{contents}`\n"
            else:
                files += f"📔`{contents}`\n"
        else:
            folders += f"📂`{contents}`\n"
    msg = msg + folders + files if files or folders else f"{msg}__empty path__"
    PATH.clear()
    PATH.append(path)
    return add_s(msg, num)


# BACK
@catub.tgbot.on(CallbackQuery(pattern=r"fmback"))
@check_owner
async def back(event):
    path = PATH[0]
    paths = path.split("/")
    if paths[-1] == "":
        paths.pop()
    paths.pop()
    npath = "".join(f"{ii}/" for ii in paths)
    num = 1
    msg, buttons = get_manager(npath, num)
    await asyncio.sleep(1)
    await event.edit(msg, buttons=buttons)


# UP
@catub.tgbot.on(CallbackQuery(pattern=r"fmup_(.*)"))
@check_owner
async def up(event):
    num = event.pattern_match.group(1).decode("UTF-8")
    if num == "File":
        await event.answer("Its a File dummy!", alert=True)
    else:
        num1 = int(num) - 1
        path = PATH[0]
        msg, buttons = get_manager(path, num1)
        await asyncio.sleep(1)
        await event.edit(msg, buttons=buttons)


# DOWN
@catub.tgbot.on(CallbackQuery(pattern=r"fmdown_(.*)"))
@check_owner
async def down(event):
    num = event.pattern_match.group(1).decode("UTF-8")
    if num == "File":
        await event.answer("Its a file dummy!", alert=True)
    else:
        path = PATH[0]
        num1 = int(num) + 1
        msg, buttons = get_manager(path, num1)
        await asyncio.sleep(1)
        await event.edit(msg, buttons=buttons)


# FORTH
@catub.tgbot.on(CallbackQuery(pattern=r"fmforth_(.*)"))
@check_owner
async def forth(event):
    npath = event.pattern_match.group(1).decode("UTF-8")
    if npath == "File":
        await event.answer("Its a file dummy!", alert=True)
    else:
        path = PATH[0]
        npath = npath[2:-4]
        rpath = f"{path}/{npath}"
        num = 1
        msg, buttons = get_manager(rpath, num)
        await asyncio.sleep(1)
        await event.edit(msg, buttons=buttons)


# REMOVE
@catub.tgbot.on(CallbackQuery(pattern=r"fmrem_(.*)"))
@check_owner
async def remove(event):
    fn, num = (event.pattern_match.group(1).decode("UTF-8")).split("|", 1)
    path = PATH[0]
    if fn == "File":
        paths = path.split("/")
        if paths[-1] == "":
            paths.pop()
        paths.pop()
        npath = "".join(f"{ii}/" for ii in paths)
        rpath = path
    else:
        n_path = fn[2:-4]
        rpath = f"{path}/{n_path}"
        npath = path
    msg, buttons = get_manager(npath, num)
    await asyncio.sleep(1)
    await event.edit(msg, buttons=buttons)
    await _catutils.runcmd(f"rm -rf '{rpath}'")
    await event.answer(f"{rpath} removed successfully...")


# SEND
@catub.tgbot.on(CallbackQuery(pattern=r"fmsend"))
@check_owner
async def send(event):
    path = PATH[0]
    startTime = time.time()
    attributes, mime_type = get_attributes(str(path))
    ul = io.open(Path(path), "rb")
    uploaded = await event.client.fast_upload_file(
        file=ul,
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(
                d,
                t,
                event,
                startTime,
                "trying to upload",
                file_name=os.path.basename(Path(path)),
            )
        ),
    )
    ul.close()
    media = types.InputMediaUploadedDocument(
        file=uploaded,
        mime_type=mime_type,
        attributes=attributes,
        force_file=False,
        thumb=(await event.client.upload_file(thumb_image_path) if thumb_image_path else None),
    )
    await event.edit("hi", file=media)


# CUT
@catub.tgbot.on(CallbackQuery(pattern=r"fmcut_(.*)"))
@check_owner
async def cut(event):
    f, n = (event.pattern_match.group(1).decode("UTF-8")).split("|", 1)
    if CC:
        return await event.answer(f"Paste {CC[1]} first")
    if f == "File":
        npath = PATH[0]
        paths = npath.split("/")
        if paths[-1] == "":
            paths.pop()
        paths.pop()
        path = "".join(f"{ii}/" for ii in paths)
        CC.append("cut")
        CC.append(npath)
        await event.answer(f"Moving {npath} ...")
    else:
        path = PATH[0]
        npath = f[2:-4]
        rpath = f"{path}/{npath}"
        CC.append("cut")
        CC.append(rpath)
        await event.answer(f"Moving {rpath} ...")
    msg, buttons = get_manager(path, n)
    await asyncio.sleep(1)
    await event.edit(msg, buttons=buttons)


# COPY
@catub.tgbot.on(CallbackQuery(pattern=r"fmcopy_(.*)"))
@check_owner
async def copy(event):
    f, n = (event.pattern_match.group(1).decode("UTF-8")).split("|", 1)
    if CC:
        return await event.answer(f"Paste {CC[1]} first")
    if f == "File":
        npath = PATH[0]
        paths = npath.split("/")
        if paths[-1] == "":
            paths.pop()
        paths.pop()
        path = "".join(f"{ii}/" for ii in paths)
        CC.append("copy")
        CC.append(npath)
        await event.answer(f"Copying {path} ...")
    else:
        path = PATH[0]
        npath = f[2:-4]
        rpath = f"{path}/{npath}"
        CC.append("copy")
        CC.append(rpath)
        await event.answer(f"Copying {rpath} ...")
    msg, buttons = get_manager(path, n)
    await asyncio.sleep(1)
    await event.edit(msg, buttons=buttons)


# PASTE
@catub.tgbot.on(CallbackQuery(pattern=r"fmpaste_(.*)"))
@check_owner
async def paste(event):
    n = event.pattern_match.group(1).decode("UTF-8")
    if CC:
        path = PATH[0]
        cmd = f"mv '{CC[1]}' '{path}'" if CC[0] == "cut" else f"cp '{CC[1]}' '{path}'"
        await _catutils.runcmd(cmd)
        msg, buttons = get_manager(path, n)
        await event.edit(msg, buttons=buttons)
        CC.clear
    else:
        await event.answer("You aint copied anything to paste")
