"""Get the info your system. Using .neofetch then .sysd"""

# .spc command is ported from  alfianandaa/ProjectAlf

import platform
import re
import sys
from datetime import datetime

import psutil
from telethon import __version__

from userbot import catub

from ..core.managers import edit_or_reply
from ..helpers.utils import _catutils

plugin_category = "tools"


def get_size(inputbytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if inputbytes < factor:
            return f"{inputbytes:.2f}{unit}{suffix}"
        inputbytes /= factor


@catub.cat_cmd(
    pattern=r"spc$",
    command=("spc", plugin_category),
    info={
        "header": "To show system specification.",
        "usage": "{tr}spc",
    },
)
async def psu(event):
    "shows system specification"
    uname = platform.uname()
    softw = "**System Information**\n"
    softw += f"`System   : {uname.system}`\n"
    softw += f"`Release  : {uname.release}`\n"
    softw += f"`Version  : {uname.version}`\n"
    softw += f"`Machine  : {uname.machine}`\n"
    # Boot Time
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    softw += f"`Boot Time: {bt.day}/{bt.month}/{bt.year}  {bt.hour}:{bt.minute}:{bt.second}`\n"
    # CPU Cores
    cpuu = "**CPU Info**\n"
    cpuu += f"`Physical cores   : {str(psutil.cpu_count(logical=False))}" + "`\n"
    cpuu += f"`Total cores      : {str(psutil.cpu_count(logical=True))}" + "`\n"
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    cpuu += f"`Max Frequency    : {cpufreq.max:.2f}Mhz`\n"
    cpuu += f"`Min Frequency    : {cpufreq.min:.2f}Mhz`\n"
    cpuu += f"`Current Frequency: {cpufreq.current:.2f}Mhz`\n\n"
    # CPU usage
    cpuu += "**CPU Usage Per Core**\n"
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
        cpuu += f"`Core {i}  : {percentage}%`\n"
    cpuu += "**Total CPU Usage**\n"
    cpuu += f"`All Core: {psutil.cpu_percent()}%`\n"
    # RAM Usage
    svmem = psutil.virtual_memory()
    memm = "**Memory Usage**\n"
    memm += f"`Total     : {get_size(svmem.total)}`\n"
    memm += f"`Available : {get_size(svmem.available)}`\n"
    memm += f"`Used      : {get_size(svmem.used)}`\n"
    memm += f"`Percentage: {svmem.percent}%`\n"
    # Bandwidth Usage
    bw = "**Bandwith Usage**\n"
    bw += f"`Upload  : {get_size(psutil.net_io_counters().bytes_sent)}`\n"
    bw += f"`Download: {get_size(psutil.net_io_counters().bytes_recv)}`\n"
    help_string = f"{softw}\n"
    help_string += f"{cpuu}\n"
    help_string += f"{memm}\n"
    help_string += f"{bw}\n"
    help_string += "**Engine Info**\n"
    help_string += f"`Python {sys.version}`\n"
    help_string += f"`Telethon {__version__}`"
    await event.edit(help_string)


@catub.cat_cmd(
    pattern=r"cpu$",
    command=("cpu", plugin_category),
    info={
        "header": "To show cpu information.",
        "usage": "{tr}cpu",
    },
)
async def cpu(event):
    "shows cpu information"
    cmd = "cat /proc/cpuinfo | grep 'model name'"
    o = (await _catutils.runcmd(cmd))[0]
    await edit_or_reply(event, f"**[Cat's](tg://need_update_for_some_feature/) CPU Model:**\n{o}")


@catub.cat_cmd(
    pattern=r"(neofetch|sysd)$",
    command=("sysd", plugin_category),
    info={
        "header": "Shows system information using neofetch",
        "usage": "{tr}sysd",
    },
)
async def sysdetails(sysd):
    "Shows system information using neofetch"
    catevent = await edit_or_reply(sysd, "`Fetching system information.`")
    cmd = "git clone https://github.com/dylanaraps/neofetch.git"
    await _catutils.runcmd(cmd)
    neo = "neofetch/neofetch --color_blocks off --bold off --cpu_temp C --cpu_speed on --cpu_cores physical --kernel_shorthand off"
    if sysd.pattern_match.group(1) == "sysd":
        neo = neo + " --off"
    a, b, c, d = await _catutils.runcmd(neo)
    ressult = str(a) + str(b)
    result = re.sub(r"\x1b\[[0-9;\?]*[a-zA-Z]", "", ressult)
    await edit_or_reply(catevent, f"**Neofetch Result:**\n```{result}```")


@catub.cat_cmd(
    pattern=r"neofetch",
    command=("neofetch", plugin_category),
    info={
        "header": "Shows system info using neoefetch with logo",
        "usage": "{tr}neofetch",
    },
)
async def neofetch_help(neo):
    "Shows System info using neofetch with logo"
