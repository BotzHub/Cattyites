# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import io
import sys
import traceback

from . import catub, edit_or_reply

plugin_category = "utils"


@catub.cat_cmd(
    pattern=r"calc ([\s\S]*)",
    command=("calc", plugin_category),
    info={
        "header": "To solve basic mathematics equations.",
        "description": "Solves the given maths equation by BODMAS rule.",
        "usage": "{tr}calc 2+9",
    },
)
async def calculator(event):
    "To solve basic mathematics equations."
    cmd = event.text.split(" ", maxsplit=1)[1]
    event = await edit_or_reply(event, "Calculating ...")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    san = f"print({cmd})"
    try:
        await aexec(san, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Sorry I can't find result for the given equation"
    final_output = f"**EQUATION**: `{cmd}` \n\n **SOLUTION**: \n`{evaluation}` \n"
    await event.edit(final_output)


async def aexec(code, event):
    exec("async def __aexec(event): " + "".join(f"\n {line}" for line in code.split("\n")))

    return await locals()["__aexec"](event)
