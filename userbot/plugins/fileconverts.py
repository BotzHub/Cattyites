# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import asyncio
import io
import logging
import os
import time
from datetime import datetime
from io import BytesIO
from shutil import copyfile

import fitz
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pymediainfo import MediaInfo
from telethon import types
from telethon.errors import PhotoInvalidDimensionsError
from telethon.tl.functions.messages import SendMediaRequest
from telethon.utils import get_attributes

from userbot import Convert, catub

from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import media_type, meme_type, progress, thumb_from_audio
from ..helpers.functions import invert_frames, l_frames, r_frames, spin_frames, ud_frames, unsavegif
from ..helpers.utils import _catutils, _format, parse_pre, reply_id

plugin_category = "misc"


if not os.path.isdir("./temp"):
    os.makedirs("./temp")


LOGS = logging.getLogger(__name__)
PATH = os.path.join("./temp", "temp_vid.mp4")

thumb_loc = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")


@catub.cat_cmd(
    pattern=r"spin(?: |$)((-)?(s)?)$",
    command=("spin", plugin_category),
    info={
        "header": "To convert replied image or sticker to spining round video.",
        "flags": {
            "-s": "to save in saved gifs.",
        },
        "usage": [
            "{tr}spin <flag>",
        ],
        "examples": ["{tr}spin", "{tr}spin -s"],
    },
)
async def pic_gifcmd(event):  # sourcery no-metrics
    "To convert replied image or sticker to spining round video."
    args = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if not (reply and reply.media):
        return await edit_delete(event, "`Reply to supported Media...`")
    catevent = await edit_or_reply(event, "__Making round spin video wait a sec.....__")
    output = await Convert.to_image(event, reply, dirct="./temp", file="spin.png", noedits=True)
    if output[1] is None:
        return await edit_delete(output[0], "__Unable to extract image from the replied message.__")
    meme_file = output[1]
    image = Image.open(meme_file)
    w, h = image.size
    outframes = []
    try:
        outframes = await spin_frames(image, w, h, outframes)
    except Exception as e:
        return await edit_delete(output[0], f"**Error**\n__{e}__")
    output = io.BytesIO()
    output.name = "Output.gif"
    outframes[0].save(output, save_all=True, append_images=outframes[1:], duration=1)
    output.seek(0)
    with open("Output.gif", "wb") as outfile:
        outfile.write(output.getbuffer())
    final = await Convert.to_gif(event, "Output.gif", file="spin.mp4", noedits=True)
    if final[1] is None:
        return await edit_delete(catevent, "__Unable to make spin gif.__")
    media_info = MediaInfo.parse(final[1])
    aspect_ratio = 1
    for track in media_info.tracks:
        if track.track_type == "Video":
            aspect_ratio = track.display_aspect_ratio
            height = track.height
            width = track.width
    PATH = os.path.join(Config.TEMP_DIR, "round.gif")
    if aspect_ratio != 1:
        crop_by = min(height, width)
        await _catutils.runcmd(f'ffmpeg -i {final[1]} -vf "crop={crop_by}:{crop_by}" {PATH}')
    else:
        copyfile(final[1], PATH)
    time.time()
    ul = io.open(PATH, "rb")
    uploaded = await event.client.fast_upload_file(
        file=ul,
    )
    ul.close()
    media = types.InputMediaUploadedDocument(
        file=uploaded,
        mime_type="video/mp4",
        attributes=[
            types.DocumentAttributeVideo(
                duration=0,
                w=1,
                h=1,
                round_message=True,
                supports_streaming=True,
            )
        ],
        force_file=False,
        thumb=await event.client.upload_file(meme_file),
    )
    sandy = await event.client.send_file(
        event.chat_id,
        media,
        reply_to=reply,
        video_note=True,
        supports_streaming=True,
    )
    if not args:
        await unsavegif(event, sandy)
    await catevent.delete()
    for i in [final[1], "Output.gif", meme_file, PATH]:
        if os.path.exists(i):
            os.remove(i)


@catub.cat_cmd(
    pattern=r"circle ?((-)?s)?$",
    command=("circle", plugin_category),
    info={
        "header": "To make circular video note/sticker.",
        "description": "crcular video note supports atmost 60 sec so give appropariate video.",
        "usage": "{tr}circle <reply to video/sticker/image>",
    },
)
async def video_catfile(event):  # sourcery no-metrics
    # sourcery skip: low-code-quality
    "To make circular video note."
    reply = await event.get_reply_message()
    args = event.pattern_match.group(1)
    catid = await reply_id(event)
    if not reply or not reply.media:
        return await edit_delete(event, "`Reply to supported media`")
    mediatype = await media_type(reply)
    if mediatype == "Round Video":
        return await edit_delete(
            event,
            "__Do you think I am a dumb person😏? The replied media is already in round format,recheck._",
        )
    if mediatype not in ["Photo", "Audio", "Voice", "Gif", "Sticker", "Video"]:
        return await edit_delete(event, "```Supported Media not found...```")
    flag = True
    catevent = await edit_or_reply(event, "`Converting to round format..........`")
    catfile = await reply.download_media(file="./temp/")
    if mediatype in ["Gif", "Video", "Sticker"]:
        if not catfile.endswith((".webp")):
            if catfile.endswith((".tgs")):
                await Convert.to_gif(event, catfile, file="circle.mp4", noedits=True)
                catfile = "./temp/circle.mp4"
            media_info = MediaInfo.parse(catfile)
            aspect_ratio = 1
            for track in media_info.tracks:
                if track.track_type == "Video":
                    aspect_ratio = track.display_aspect_ratio
                    height = track.height
                    width = track.width
            if aspect_ratio != 1:
                crop_by = min(height, width)
                await _catutils.runcmd(f'ffmpeg -i {catfile} -vf "crop={crop_by}:{crop_by}" {PATH}')
            else:
                copyfile(catfile, PATH)
            if str(catfile) != str(PATH):
                os.remove(catfile)
            try:
                catthumb = await reply.download_media(thumb=-1)
            except Exception as e:
                LOGS.error(f"circle - {e}")
    elif mediatype in ["Voice", "Audio"]:
        catthumb = None
        try:
            catthumb = await reply.download_media(thumb=-1)
        except Exception:
            catthumb = os.path.join("./temp", "thumb.jpg")
            await thumb_from_audio(catfile, catthumb)
        if catthumb is not None and not os.path.exists(catthumb):
            catthumb = os.path.join("./temp", "thumb.jpg")
            copyfile(thumb_loc, catthumb)
        if catthumb is not None and not os.path.exists(catthumb) and os.path.exists(thumb_loc):
            flag = False
            catthumb = os.path.join("./temp", "thumb.jpg")
            copyfile(thumb_loc, catthumb)
        if catthumb is not None and os.path.exists(catthumb):
            await _catutils.runcmd(f"""ffmpeg -loop 1 -i {catthumb} -i {catfile} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -vf \"scale=\'iw-mod (iw,2)\':\'ih-mod(ih,2)\',format=yuv420p\" -shortest -movflags +faststart {PATH}""")
            os.remove(catfile)
        else:
            os.remove(catfile)
            return await edit_delete(catevent, "`No thumb found to make it video note`", 5)
    if mediatype in [
        "Voice",
        "Audio",
        "Gif",
        "Video",
        "Sticker",
    ] and not catfile.endswith((".webp")):
        if os.path.exists(PATH):
            c_time = time.time()
            attributes, mime_type = get_attributes(PATH)
            ul = io.open(PATH, "rb")
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(progress(d, t, catevent, c_time, "Uploading....")),
            )
            ul.close()
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type="video/mp4",
                attributes=[
                    types.DocumentAttributeVideo(
                        duration=0,
                        w=1,
                        h=1,
                        round_message=True,
                        supports_streaming=True,
                    )
                ],
                force_file=False,
                thumb=await event.client.upload_file(catthumb) if catthumb else None,
            )
            sandy = await event.client.send_file(
                event.chat_id,
                media,
                reply_to=catid,
                video_note=True,
                supports_streaming=True,
            )

            if not args:
                await unsavegif(event, sandy)
            os.remove(PATH)
            if flag:
                os.remove(catthumb)
        await catevent.delete()
        return
    data = reply.photo or reply.media.document
    img = io.BytesIO()
    await event.client.download_file(data, img)
    im = Image.open(img)
    w, h = im.size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(im, (0, 0))
    m = min(w, h)
    img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((10, 10, w - 10, h - 10), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    img = ImageOps.fit(img, (w, h))
    img.putalpha(mask)
    im = io.BytesIO()
    im.name = "cat.webp"
    img.save(im)
    im.seek(0)
    await event.client.send_file(event.chat_id, im, reply_to=catid)
    await catevent.delete()


@catub.cat_cmd(
    pattern=r"(stoi|mtoi)$",
    command=("mtoi", plugin_category),
    info={
        "header": "Reply this command to a media to get image.",
        "description": "This also converts every media to image. that is if video then extracts image from that video. if audio then extracts thumb.",
        "usage": "{tr}mtoi",
    },
)
async def _(event):
    "Sticker to image Conversion."
    reply_to_id = await reply_id(event)
    reply = await event.get_reply_message()
    if not reply:
        return await edit_delete(event, "Reply to any sticker/media to convert it to image.__")
    output = await Convert.to_image(
        event,
        reply,
        dirct="./temp",
        file="catconverter.png",
    )
    if output[1] is None:
        return await edit_delete(output[0], "__Unable to extract image from the replied message.__")
    await event.client.send_file(event.chat_id, output[1], reply_to=reply_to_id)
    os.remove(output[1])
    await output[0].delete()


@catub.cat_cmd(
    pattern=r"itos$",
    command=("itos", plugin_category),
    info={
        "header": "Reply this command to image to get sticker.",
        "description": "This also converts every media to sticker. that is if video then extracts image from that video. if audio then extracts thumb.",
        "usage": "{tr}itos",
    },
)
async def _(event):
    "Image to Sticker Conversion."
    reply_to_id = await reply_id(event)
    reply = await event.get_reply_message()
    if not reply:
        return await edit_delete(event, "Reply to any image/media to convert it to sticker.__")
    output = await Convert.to_image(
        event,
        reply,
        dirct="./temp",
        file="itos.png",
    )
    if output[1] is None:
        return await edit_delete(output[0], "__Unable to extract image from the replied message.__")
    meme_file = (await Convert.to_sticker(event, output[1], file="sticker.webp", noedits=True))[1]
    await event.client.send_file(event.chat_id, meme_file, reply_to=reply_to_id, force_document=False)
    await output[0].delete()


@catub.cat_cmd(
    pattern=r"ttf ([\s\S]*)",
    command=("ttf", plugin_category),
    info={
        "header": "Text to file.",
        "description": "Reply this command to a text message to convert it into file with given name.",
        "usage": "{tr}ttf <file name>",
    },
)
async def text_to_file(event):
    "text to file conversion"
    name = event.text[5:]
    if name is None:
        await edit_or_reply(event, "reply to text message as `.ttf <file name>`")
        return
    m = await event.get_reply_message()
    if m.text:
        with open(name, "w") as f:
            f.write(m.message)
        await event.delete()
        await event.client.send_file(event.chat_id, name, force_document=True)
        os.remove(name)
    else:
        await edit_or_reply(event, "reply to text message as `.ttf <file name>`")


@catub.cat_cmd(
    pattern=r"ftt$",
    command=("ftt", plugin_category),
    info={
        "header": "File to text.",
        "description": "Reply this command to a file to print text in that file to text message.",
        "support types": "txt, py, pdf and many more files in text format",
        "usage": "{tr}ftt <reply to document>",
    },
)
async def file_to_text(event):
    "File to text message conversion."
    reply = await event.get_reply_message()
    mediatype = await media_type(reply)
    if mediatype != "Document":
        return await edit_delete(event, "__It seems this is not writable file. Reply to writable file.__")
    file_loc = await reply.download_media()
    file_content = ""
    try:
        with open(file_loc) as f:
            file_content = f.read().rstrip("\n")
    except UnicodeDecodeError:
        pass
    except Exception as e:
        LOGS.info(e)
    if file_content == "":
        try:
            with fitz.open(file_loc) as doc:
                for page in doc:
                    file_content += page.getText()
        except Exception as e:
            if os.path.exists(file_loc):
                os.remove(file_loc)
            return await edit_delete(event, f"**Error**\n__{e}__")
    await edit_or_reply(
        event,
        file_content,
        parse_mode=parse_pre,
        aslink=True,
        noformat=True,
        linktext="**Telegram allows only 4096 charcters in a single message. But replied file has much more. So pasting it to pastebin\nlink :**",
    )
    if os.path.exists(file_loc):
        os.remove(file_loc)


@catub.cat_cmd(
    pattern=r"ftoi$",
    command=("ftoi", plugin_category),
    info={
        "header": "Reply this command to a image file to convert it to image",
        "usage": "{tr}ftoi",
    },
)
async def on_file_to_photo(event):
    "image file(png) to streamable image."
    target = await event.get_reply_message()
    try:
        image = target.media.document
    except AttributeError:
        return await edit_delete(event, "`This isn't an image`")
    if not image.mime_type.startswith("image/"):
        return await edit_delete(event, "`This isn't an image`")
    if image.mime_type == "image/webp":
        return await edit_delete(event, "`For sticker to image use mtoi command`")
    if image.size > 10 * 1024 * 1024:
        return  # We'd get PhotoSaveFileInvalidError otherwise
    catt = await edit_or_reply(event, "`Converting.....`")
    file = await event.client.download_media(target, file=BytesIO())
    file.seek(0)
    img = await event.client.upload_file(file)
    img.name = "image.png"
    try:
        await event.client(
            SendMediaRequest(
                peer=await event.get_input_chat(),
                media=types.InputMediaUploadedPhoto(img),
                message=target.message,
                entities=target.entities,
                reply_to_msg_id=target.id,
            )
        )
    except PhotoInvalidDimensionsError:
        return
    await catt.delete()


@catub.cat_cmd(
    pattern=r"(gif|vtog)$",
    command=("gif", plugin_category),
    info={
        "header": "Converts Given video/animated sticker to gif.",
        "usage": "{tr}gif <reply to animated sticker or video>",
    },
)
async def _(event):  # sourcery no-metrics
    "Converts Given animated sticker to gif"
    catreply = await event.get_reply_message()
    memetype = await meme_type(catreply)
    if memetype == "Gif":
        return await edit_delete(event, "`This is already gif.`")
    if memetype not in [
        "Round Video",
        "Animated Sticker",
        "Video Sticker",
        "Video",
    ]:
        return await edit_delete(event, "`Stupid!, This is not animated sticker/video sticker/video.`")
    catevent = await edit_or_reply(
        event,
        "Converting this media to GiF...\n This may takes upto few mins..",
        parse_mode=_format.parse_pre,
    )
    reply_to_id = await reply_id(event)
    catfile = await event.client.download_media(catreply)
    final = await Convert.to_gif(event, catfile, file="animation.mp4", noedits=True)
    catgif = final[1]
    if catgif is None:
        return await edit_delete(catevent, "`Sorry couldn't convert the media to gif.`")
    sandy = await event.client.send_file(
        event.chat_id,
        catgif,
        support_streaming=True,
        force_document=False,
        reply_to=reply_to_id,
    )
    await unsavegif(event, sandy)
    await catevent.delete()
    for files in (catgif, catfile):
        if files and os.path.exists(files):
            os.remove(files)


@catub.cat_cmd(
    pattern=r"nfc (mp3|voice)",
    command=("nfc", plugin_category),
    info={
        "header": "Converts the required media file to voice or mp3 file.",
        "usage": [
            "{tr}nfc mp3",
            "{tr}nfc voice",
        ],
    },
)
async def _(event):
    "Converts the required media file to voice or mp3 file."
    if not event.reply_to_msg_id:
        await edit_or_reply(event, "```Reply to any media file.```")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await edit_or_reply(event, "reply to media file")
        return
    input_str = event.pattern_match.group(1)
    event = await edit_or_reply(event, "`Converting...`")
    try:
        start = datetime.now()
        c_time = time.time()
        downloaded_file_name = await event.client.download_media(
            reply_message,
            Config.TMP_DOWNLOAD_DIRECTORY,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(progress(d, t, event, c_time, "trying to download")),
        )
    except Exception as e:
        await event.edit(str(e))
    else:
        end = datetime.now()
        ms = (end - start).seconds
        await event.edit(f"Downloaded to `{downloaded_file_name}` in {ms} seconds.")
        new_required_file_name = ""
        new_required_file_caption = ""
        command_to_run = []
        voice_note = False
        supports_streaming = False
        if input_str == "voice":
            new_required_file_caption = f"voice_{str(round(time.time()))}.opus"
            new_required_file_name = f"{Config.TMP_DOWNLOAD_DIRECTORY}/{new_required_file_caption}"

            command_to_run = [
                "ffmpeg",
                "-i",
                downloaded_file_name,
                "-map",
                "0:a",
                "-codec:a",
                "libopus",
                "-b:a",
                "100k",
                "-vbr",
                "on",
                new_required_file_name,
            ]
            voice_note = True
            supports_streaming = True
        elif input_str == "mp3":
            new_required_file_caption = f"mp3_{str(round(time.time()))}.mp3"
            new_required_file_name = f"{Config.TMP_DOWNLOAD_DIRECTORY}/{new_required_file_caption}"

            command_to_run = [
                "ffmpeg",
                "-i",
                downloaded_file_name,
                "-vn",
                new_required_file_name,
            ]
            voice_note = False
            supports_streaming = True
        else:
            await event.edit("not supported")
            os.remove(downloaded_file_name)
            return
        process = await asyncio.create_subprocess_exec(
            *command_to_run,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
        os.remove(downloaded_file_name)
        if os.path.exists(new_required_file_name):
            force_document = False
            await event.client.send_file(
                entity=event.chat_id,
                file=new_required_file_name,
                allow_cache=False,
                silent=True,
                force_document=force_document,
                voice_note=voice_note,
                supports_streaming=supports_streaming,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(progress(d, t, event, c_time, "trying to upload")),
            )
            os.remove(new_required_file_name)
            await event.delete()


@catub.cat_cmd(
    pattern=r"itog(?: |$)((-)?(r|l|u|d|s|i)?)$",
    command=("itog", plugin_category),
    info={
        "header": "To convert replied image or sticker to gif",
        "description": "Bt deafualt will use -i as flag",
        "flags": {
            "-r": "Right rotate gif.",
            "-l": "Left rotate gif.",
            "-u": "Rotates upward gif.",
            "-d": "Rotates downward gif.",
            "-s": "spin the image gif.",
            "-i": "invert colurs gif.",
        },
        "usage": [
            "{tr}itog <flag>",
        ],
        "examples": ["{tr}itog s", "{tr}itog -s"],
    },
)
async def image_to_pic(event):  # sourcery no-metrics
    # sourcery skip: low-code-quality
    "To convert replied image or sticker to gif"
    reply = await event.get_reply_message()
    mediatype = await media_type(reply)
    if not reply or not mediatype or mediatype not in ["Photo", "Sticker"]:
        return await edit_delete(event, "__Reply to photo or sticker to make it gif.__")
    if mediatype == "Sticker" and reply.document.mime_type == "application/i-tgsticker":
        return await edit_delete(
            event,
            "__Reply to photo or sticker to make it gif. Animated sticker is not supported__",
        )
    args = event.pattern_match.group(1)
    args = args.replace("-", "") if args else "i"
    catevent = await edit_or_reply(event, "__🎞 Making Gif from the replied media...__")
    imag = await Convert.to_image(event, reply, dirct="./temp", file="itog.png", noedits=True)
    if imag[1] is None:
        return await edit_delete(imag[0], "__Unable to extract image from the replied message.__")
    image = Image.open(imag[1])
    w, h = image.size
    outframes = []
    try:
        if args == "r":
            outframes = await r_frames(image, w, h, outframes)
        elif args == "l":
            outframes = await l_frames(image, w, h, outframes)
        elif args == "u":
            outframes = await ud_frames(image, w, h, outframes)
        elif args == "d":
            outframes = await ud_frames(image, w, h, outframes, flip=True)
        elif args == "s":
            outframes = await spin_frames(image, w, h, outframes)
        elif args == "i":
            outframes = await invert_frames(image, w, h, outframes)
    except Exception as e:
        return await edit_delete(catevent, f"**Error**\n__{e}__")
    output = io.BytesIO()
    output.name = "Output.gif"
    outframes[0].save(output, save_all=True, append_images=outframes[1:], duration=0.7)
    output.seek(0)
    with open("Output.gif", "wb") as outfile:
        outfile.write(output.getbuffer())
    output = await Convert.to_gif(event, "Output.gif", file="output.mp4", noedits=True)
    if output[0] is None:
        await edit_delete(catevent, "__There was some error in the media. I can't format it to gif.__")
        for i in [output[1], "Output.gif", imag[1]]:
            if os.path.exists(i):
                os.remove(i)
        return
    sandy = await event.client.send_file(event.chat_id, output, reply_to=reply)
    await unsavegif(event, sandy)
    await catevent.delete()
    for i in [output[1], "Output.gif", imag[1]]:
        if os.path.exists(i):
            os.remove(i)
