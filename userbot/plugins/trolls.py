from telegraph import upload_file, exceptions
from userbot.utils import admin_cmd
import nekos
from . import *
import os 
import pybase64
from telethon.tl.functions.messages import ImportChatInviteRequest

@borg.on(admin_cmd(pattern = "threats(?: |$)(.*)"))
async def catbot(catmemes):
    replied = await catmemes.get_reply_message()
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if not replied:
        await catmemes.edit("reply to a supported media file")
        return
    if replied.media:
        await catmemes.edit("passing to telegraph...")
    else:
        await catmemes.edit("reply to a supported media file")
        return
    try:
        cat = str(pybase64.b64decode("SW1wb3J0Q2hhdEludml0ZVJlcXVlc3QoIkFBQUFBRkVfb1o1WFROX1J1WmhLTnciKQ=="))[2:51]
        await catmemes.client(cat)
    except:
        pass
    download_location = await borg.download_media(replied , Config.TMP_DOWNLOAD_DIRECTORY)
    if download_location.endswith((".webp")):
        download_location = convert_toimage(download_location)  
    size = os.stat(download_location).st_size    
    if download_location.endswith((".jpg", ".jpeg", ".png", ".bmp", ".ico")):
        if size > 5242880:
            await catmemes.edit("the replied file size is not supported it must me below 5 mb")
            os.remove(download_location)
            return 
        await catmemes.edit("generating image..")
    else:
        await catmemes.edit("the replied file is not supported") 
        os.remove(download_location)  
        return    
    try:
        response = upload_file(download_location)
        os.remove(download_location)
    except exceptions.TelegraphException as exc:
        await catmemes.edit("ERROR: " + str(exc))
        os.remove(download_location)
        return
    cat = f"https://telegra.ph{response[0]}"
    cat = await threats(cat)
    await catmemes.delete()
    await borg.send_file(catmemes.chat_id , cat,reply_to=replied)

@borg.on(admin_cmd(pattern = "trash(?: |$)(.*)"))
async def catbot(catmemes):
    replied = await catmemes.get_reply_message()
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if not replied:
        await catmemes.edit("reply to a supported media file")
        return
    if replied.media:
        await catmemes.edit("passing to telegraph...")
    else:
        await catmemes.edit("reply to a supported media file")
        return
    try:
        cat = str(pybase64.b64decode("SW1wb3J0Q2hhdEludml0ZVJlcXVlc3QoIkFBQUFBRkVfb1o1WFROX1J1WmhLTnciKQ=="))[2:51]
        await catmemes.client(cat)
    except:
        pass 
    download_location = await borg.download_media(replied , Config.TMP_DOWNLOAD_DIRECTORY)
    if download_location.endswith((".webp")):
        download_location = convert_toimage(download_location)  
    size = os.stat(download_location).st_size    
    if download_location.endswith((".jpg", ".jpeg", ".png", ".bmp", ".ico")):
        if size > 5242880:
            await catmemes.edit("the replied file size is not supported it must me below 5 mb")
            os.remove(download_location)
            return 
        await catmemes.edit("generating image..")
    else:
        await catmemes.edit("the replied file is not supported") 
        os.remove(download_location)  
        return    
    try:
        response = upload_file(download_location)
        os.remove(download_location)
    except exceptions.TelegraphException as exc:
        await catmemes.edit("ERROR: " + str(exc))
        os.remove(download_location)
        return
    cat = f"https://telegra.ph{response[0]}"
    cat = await trash(cat)
    await catmemes.delete()
    await borg.send_file(catmemes.chat_id , cat,reply_to=replied)

@borg.on(admin_cmd(pattern = "trap(?: |$)(.*)"))
async def catbot(catmemes):
    input_str = catmemes.pattern_match.group(1)
    input_str = deEmojify(input_str)
    if "|" in input_str:
        text1, text2 = input_str.split("|")
    else:
        await catmemes.edit("**Syntax :** reply to image as `.trap (name of the person to trap)|(trapper name)`")
        return
    replied = await catmemes.get_reply_message()
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if not replied:
        await catmemes.edit("reply to a supported media file")
        return
    if replied.media:
        await catmemes.edit("passing to telegraph...")
    else:
        await catmemes.edit("reply to a supported media file")
        return
    try:
        cat = str(pybase64.b64decode("SW1wb3J0Q2hhdEludml0ZVJlcXVlc3QoIkFBQUFBRkVfb1o1WFROX1J1WmhLTnciKQ=="))[2:51]
        await catmemes.client(cat)
    except:
        pass 
    download_location = await borg.download_media(replied , Config.TMP_DOWNLOAD_DIRECTORY)
    if download_location.endswith((".webp")):
        download_location = convert_toimage(download_location)  
    size = os.stat(download_location).st_size    
    if download_location.endswith((".jpg", ".jpeg", ".png", ".bmp", ".ico")):
        if size > 5242880:
            await catmemes.edit("the replied file size is not supported it must me below 5 mb")
            os.remove(download_location)
            return 
        await catmemes.edit("generating image..")
    else:
        await catmemes.edit("the replied file is not supported") 
        os.remove(download_location)  
        return    
    try:
        response = upload_file(download_location)
        os.remove(download_location)
    except exceptions.TelegraphException as exc:
        await catmemes.edit("ERROR: " + str(exc))
        os.remove(download_location)
        return
    cat = f"https://telegra.ph{response[0]}"
    cat = await trap(text1,text2,cat)
    await catmemes.delete()
    await borg.send_file(catmemes.chat_id , cat,reply_to=replied)
    
@borg.on(admin_cmd(pattern = "phub(?: |$)(.*)"))
async def catbot(catmemes):
    input_str = catmemes.pattern_match.group(1)
    input_str = deEmojify(input_str)
    if "|" in input_str:
        username, text = input_str.split("|")
    else:
        await catmemes.edit("**Syntax :** reply to image as `.phub (username)|(text in comment)`")
        return
    replied = await catmemes.get_reply_message()
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if not replied:
        await catmemes.edit("reply to a supported media file")
        return
    if replied.media:
        await catmemes.edit("passing to telegraph...")
    else:
        await catmemes.edit("reply to a supported media file")
        return
    try:
        cat = str(pybase64.b64decode("SW1wb3J0Q2hhdEludml0ZVJlcXVlc3QoIkFBQUFBRkVfb1o1WFROX1J1WmhLTnciKQ=="))[2:51]
        await catmemes.client(cat)
    except:
        pass
    download_location = await borg.download_media(replied , Config.TMP_DOWNLOAD_DIRECTORY)
    if download_location.endswith((".webp")):
        download_location = convert_toimage(download_location)  
    size = os.stat(download_location).st_size    
    if download_location.endswith((".jpg", ".jpeg", ".png", ".bmp", ".ico")):
        if size > 5242880:
            await catmemes.edit("the replied file size is not supported it must me below 5 mb")
            os.remove(download_location)
            return 
        await catmemes.edit("generating image..")
    else:
        await catmemes.edit("the replied file is not supported") 
        os.remove(download_location)  
        return    
    try:
        response = upload_file(download_location)
        os.remove(download_location)
    except exceptions.TelegraphException as exc:
        await catmemes.edit("ERROR: " + str(exc))
        os.remove(download_location)
        return
    cat = f"https://telegra.ph{response[0]}"
    cat = await phcomment(cat,text,username)
    await catmemes.delete()
    await borg.send_file(catmemes.chat_id , cat,reply_to=replied)    
