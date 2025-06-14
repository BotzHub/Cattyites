# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import asyncio
import io
import os
import time
import zipfile
from datetime import datetime
from pathlib import Path
from tarfile import is_tarfile
from tarfile import open as tar_open

from telethon import types
from telethon.utils import get_extension

from ..Config import Config
from ..helpers.utils import _catutils
from . import catub, edit_delete, edit_or_reply, progress
from .upload import UPLOAD_, upload

thumb_image_path = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")
plugin_category = "misc"


def zipdir(dirName):
    filePaths = []
    for root, directories, files in os.walk(dirName):
        for filename in files:
            filePath = os.path.join(root, filename)
            filePaths.append(filePath)
    return filePaths


async def upload_unpacked(event, text_event, path):
    await edit_or_reply(text_event, "`Uploading file .....`")
    UPLOAD_.uploaded = 0
    await upload(path, event, text_event)
    await _catutils.runcmd(f"rm -rf {path}")


@catub.cat_cmd(
    pattern=r"zip(?:\s|$)([\s\S]*)",
    command=("zip", plugin_category),
    info={
        "header": "To compress the file/folders",
        "description": "Will create a zip file for the given file path or folder path",
        "usage": [
            "{tr}zip <file/folder path>",
        ],
        "examples": ["{tr}zip downloads", "{tr}zip sample_config.py"],
    },
)
async def zip_file(event):
    "To create zip file"
    input_str = event.pattern_match.group(1)
    if not input_str:
        return await edit_delete(event, "`Provide file path to zip`")
    start = datetime.now()
    if not os.path.exists(Path(input_str)):
        return await edit_or_reply(
            event,
            f"There is no such directory or file with the name `{input_str}` check again",
        )
    if os.path.isfile(Path(input_str)):
        return await edit_delete(event, "`File compressing is not implemented yet`")
    mone = await edit_or_reply(event, "`Zipping in progress....`")
    filePaths = zipdir(input_str)
    filepath = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, os.path.basename(Path(input_str)))
    zip_file_var = zipfile.ZipFile(f"{filepath}.zip", "w")
    with zip_file_var:
        for file in filePaths:
            zip_file_var.write(file)
    end = datetime.now()
    ms = (end - start).seconds
    await mone.edit(f"Zipped the path `{input_str}` into `{filepath}.zip` in __{ms}__ Seconds")


@catub.cat_cmd(
    pattern=r"tar(?:\s|$)([\s\S]*)",
    command=("tar", plugin_category),
    info={
        "header": "To compress the file/folders to tar file",
        "description": "Will create a tar file for the given file path or folder path",
        "usage": [
            "{tr}tar <file/folder path>",
        ],
        "examples": ["{tr}tar downloads", "{tr}tar sample_config.py"],
    },
)
async def tar_file(event):
    "To create tar file"
    input_str = event.pattern_match.group(1)
    if not input_str:
        return await edit_delete(event, "`Provide file path to compress`")
    if not os.path.exists(Path(input_str)):
        return await edit_or_reply(
            event,
            f"There is no such directory or file with the name `{input_str}` check again",
        )
    if os.path.isfile(Path(input_str)):
        return await edit_delete(event, "`File compressing is not implemented yet`")
    mone = await edit_or_reply(event, "`Tar creation in progress....`")
    start = datetime.now()
    filePaths = zipdir(input_str)
    filepath = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, os.path.basename(Path(input_str)))
    destination = f"{filepath}.tar.gz"
    tar_file_var = tar_open(destination, "w:gz")
    with tar_file_var:
        for file in filePaths:
            tar_file_var.add(file)
    end = datetime.now()
    ms = (end - start).seconds
    await mone.edit(f"Created a tar file for the given path {input_str} as `{destination}` in __{ms}__ Seconds")


@catub.cat_cmd(
    pattern=r"unzip(?:\s|$)([\s\S]*)",
    command=("unzip", plugin_category),
    info={
        "header": "To unpack the given zip file",
        "description": "Reply to a zip file or provide zip file path with command to unzip the given file",
        "flags": {"u": "Upload files after unpacking."},
        "usage": [
            "{tr}unzip <reply/file path>",
            "{tr}unzip -u <reply/file path>",
        ],
    },
)
async def unzip_file(event):  # sourcery no-metrics
    # sourcery skip: low-code-quality
    "To unpack the zip file"
    upload_flag = False
    input_str = event.pattern_match.group(1)
    if input_str and "-u" in input_str:
        upload_flag = True
        input_str = input_str.replace("-u", "").strip()
    if input_str:
        path = Path(input_str)
        if os.path.exists(path):
            start = datetime.now()
            if not zipfile.is_zipfile(path):
                return await edit_delete(event, f"`The Given path {path} is not zip file to unpack`")

            mone = await edit_or_reply(event, "`Unpacking....`")
            destination = os.path.join(
                Config.TMP_DOWNLOAD_DIRECTORY,
                os.path.splitext(os.path.basename(path))[0],
            )
            with zipfile.ZipFile(path, "r") as zip_ref:
                zip_ref.extractall(destination)
            end = datetime.now()
            ms = (end - start).seconds
            await edit_or_reply(
                mone,
                f"unzipped and stored to `{destination}` \n**Time Taken :** `{ms} seconds`",
            )
            if upload_flag:
                await upload_unpacked(event, mone, destination)
        else:
            await edit_delete(event, f"I can't find that path `{input_str}`", 10)
    elif event.reply_to_msg_id:
        start = datetime.now()
        reply = await event.get_reply_message()
        ext = get_extension(reply.document)
        if ext != ".zip":
            return await edit_delete(
                event,
                "`The replied file is not a zip file recheck the replied message`",
            )
        mone = await edit_or_reply(event, "`Unpacking....`")
        for attr in getattr(reply.document, "attributes", []):
            if isinstance(attr, types.DocumentAttributeFilename):
                filename = attr.file_name
        filename = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, filename)
        c_time = time.time()
        try:
            dl = io.FileIO(filename, "a")
            await event.client.fast_download_file(
                location=reply.document,
                out=dl,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(progress(d, t, mone, c_time, "trying to download")),
            )
            dl.close()
        except Exception as e:
            return await edit_delete(mone, f"**Error:**\n__{e}__")
        await edit_or_reply(mone, "`Download finished Unpacking now`")
        destination = os.path.join(
            Config.TMP_DOWNLOAD_DIRECTORY,
            os.path.splitext(os.path.basename(filename))[0],
        )
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(destination)
        end = datetime.now()
        ms = (end - start).seconds
        await edit_or_reply(
            mone,
            f"unzipped and stored to `{destination}` \n**Time Taken :** `{ms} seconds`",
        )
        os.remove(filename)
        if upload_flag:
            await upload_unpacked(event, mone, destination)
    else:
        await edit_delete(
            event,
            "`Either reply to the zipfile or provide path of zip file along with command`",
        )


@catub.cat_cmd(
    pattern=r"untar(?:\s|$)([\s\S]*)",
    command=("untar", plugin_category),
    info={
        "header": "To unpack the given tar file",
        "description": "Reply to a tar file or provide tar file path with command to unpack the given tar file",
        "flags": {"u": "Upload files after unpacking."},
        "usage": [
            "{tr}untar <reply/file path>",
            "{tr}untar -u <reply/file path>",
        ],
    },
)
async def untar_file(event):  # sourcery no-metrics
    # sourcery skip: low-code-quality
    "To unpack the tar file"
    upload_flag = False
    input_str = event.pattern_match.group(1)
    if input_str and "-u" in input_str:
        upload_flag = True
        input_str = input_str.replace("-u", "").strip()
    if input_str:
        path = Path(input_str)
        if os.path.exists(path):
            start = datetime.now()
            if not is_tarfile(path):
                return await edit_delete(event, f"`The Given path {path} is not tar file to unpack`")

            mone = await edit_or_reply(event, "`Unpacking....`")
            destination = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, (os.path.basename(path).split("."))[0])
            if not os.path.exists(destination):
                os.mkdir(destination)
            file = tar_open(path)
            # extracting file
            file.extractall(destination)
            file.close()
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit(
                f"**Time Taken :** `{ms} seconds`\
                \nUnpacked the input path `{input_str}` and stored to `{destination}`"
            )
            if upload_flag:
                await upload_unpacked(event, mone, destination)
        else:
            await edit_delete(event, f"I can't find that path `{input_str}`", 10)
    elif event.reply_to_msg_id:
        start = datetime.now()
        reply = await event.get_reply_message()
        mone = await edit_or_reply(event, "`Unpacking....`")
        for attr in getattr(reply.document, "attributes", []):
            if isinstance(attr, types.DocumentAttributeFilename):
                filename = attr.file_name
        filename = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, filename)
        c_time = time.time()
        try:
            dl = io.FileIO(filename, "a")
            await event.client.fast_download_file(
                location=reply.document,
                out=dl,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(progress(d, t, mone, c_time, "trying to download")),
            )
            dl.close()
        except Exception as e:
            return await edit_delete(mone, f"**Error:**\n__{e}__")
        if not is_tarfile(filename):
            return await edit_delete(mone, "`The replied file is not tar file to unpack it recheck it`")
        await mone.edit("`Download finished Unpacking now`")
        destination = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, (os.path.basename(filename).split("."))[0])

        if not os.path.exists(destination):
            os.mkdir(destination)
        file = tar_open(filename)
        # extracting file
        file.extractall(destination)
        file.close()
        end = datetime.now()
        ms = (end - start).seconds
        await mone.edit(
            f"**Time Taken :** `{ms} seconds`\
                \nUnpacked the replied file and stored to `{destination}`"
        )
        os.remove(filename)
        if upload_flag:
            await upload_unpacked(event, mone, destination)
    else:
        await edit_delete(
            event,
            "`Either reply to the tarfile or provide path of tarfile along with command`",
        )
