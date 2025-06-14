# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.

# This file is part of: https://github.com/TgCatUB/catuserbot
# and is released under the "GNU v3.0 License Agreement".

# Please see: https://github.com/TgCatUB/catuserbot/blob/master/LICENSE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import asyncio
import contextlib
import os
import sys
from asyncio.exceptions import CancelledError

import heroku3
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from userbot import HEROKU_APP, UPSTREAM_REPO_URL, catub

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _catutils
from ..sql_helper.global_collection import add_to_collectionlist, del_keyword_collectionlist, get_collectionlist_items

plugin_category = "tools"
cmdhd = Config.COMMAND_HAND_LER
ENV = bool(os.environ.get("ENV", False))
LOGS = logging.getLogger(__name__)
# -- Constants -- #

HEROKU_APP_NAME = Config.HEROKU_APP_NAME or None
HEROKU_API_KEY = Config.HEROKU_API_KEY or None
Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
BADCAT = Config.BADCAT
heroku_api = "https://api.heroku.com"

UPSTREAM_REPO_BRANCH = Config.UPSTREAM_REPO_BRANCH

REPO_REMOTE_NAME = "temponame"
IFFUCI_ACTIVE_BRANCH_NAME = "master"
NO_HEROKU_APP_CFGD = "no heroku application found, but a key given? 😕 "
HEROKU_GIT_REF_SPEC = "HEAD:refs/heads/master"
RESTARTING_APP = "re-starting heroku application"
IS_SELECTED_DIFFERENT_BRANCH = "looks like a custom branch {branch_name} " "is being used:\n" "in this case, Updater is unable to identify the branch to be updated." "please check out to an official branch, and re-start the updater."

# -- Constants End -- #

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "requirements.txt")


async def gen_chlog(repo, diff):
    d_form = "%d/%m/%y"
    return "".join(f"  • {c.summary} ({c.committed_datetime.strftime(d_form)}) <{c.author}>\n" for c in repo.iter_commits(diff))


async def print_changelogs(event, ac_br, changelog):
    changelog_str = f"**New UPDATE available for [{ac_br}]:\n\nCHANGELOG:**\n`{changelog}`"
    if len(changelog_str) > 4096:
        await event.edit("`Changelog is too big, view the file to see it.`")
        with open("output.txt", "w+") as file:
            file.write(changelog_str)
        await event.client.send_file(
            event.chat_id,
            "output.txt",
            reply_to=event.id,
        )
        os.remove("output.txt")
    else:
        await event.client.send_message(
            event.chat_id,
            changelog_str,
            reply_to=event.id,
        )
    return True


async def update_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "--upgrade", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


async def update_bot(event, repo, ups_rem, ac_br):
    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    await update_requirements()
    sandy = await event.edit("`Successfully Updated!\n" "Bot is restarting... Wait for a minute!`")
    if os.path.exists("config.py"):
        from userbot.plugins.vps import reload_codebase

        await reload_codebase()
    await event.client.reload(sandy)


async def deploy(event, repo, ups_rem, ac_br, txt):
    if HEROKU_API_KEY is None:
        return await event.edit("`Please set up`  **HEROKU_API_KEY**  ` Var...`")
    heroku = heroku3.from_key(HEROKU_API_KEY)
    heroku_applications = heroku.apps()
    if HEROKU_APP_NAME is None:
        await event.edit("`Please set up the` **HEROKU_APP_NAME** `Var`" " to be able to deploy your userbot...`")
        repo.__del__()
        return
    heroku_app = next(
        (app for app in heroku_applications if app.name == HEROKU_APP_NAME),
        None,
    )

    if heroku_app is None:
        await event.edit(f"{txt}\n" "`Invalid Heroku credentials for deploying userbot dyno.`")
        return repo.__del__()
    sandy = await event.edit("`Userbot dyno build in progress, please wait until the process finishes it usually takes 4 to 5 minutes .`")
    try:
        ulist = get_collectionlist_items()
        for i in ulist:
            if i == "restart_update":
                del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
    try:
        add_to_collectionlist("restart_update", [sandy.chat_id, sandy.id])
    except Exception as e:
        LOGS.error(e)
    ups_rem.fetch(ac_br)
    repo.git.reset("--hard", "FETCH_HEAD")
    heroku_git_url = heroku_app.git_url.replace("https://", f"https://api:{HEROKU_API_KEY}@")

    if "heroku" in repo.remotes:
        remote = repo.remote("heroku")
        remote.set_url(heroku_git_url)
    else:
        remote = repo.create_remote("heroku", heroku_git_url)
    try:
        remote.push(refspec="HEAD:refs/heads/master", force=True)
    except Exception as error:
        await event.edit(f"{txt}\n**Error log:**\n`{error}`")
        return repo.__del__()
    build_status = heroku_app.builds(order_by="created_at", sort="desc")[0]
    if build_status.status == "failed":
        return await edit_delete(event, "`Build failed!\n" "Cancelled or there were some errors...`")
    try:
        remote.push("master:main", force=True)
    except Exception as error:
        await event.edit(f"{txt}\n**Here is the error log:**\n`{error}`")
        return repo.__del__()
    await event.edit("`Deploy was failed. So restarting to update`")
    with contextlib.suppress(CancelledError):
        await event.client.disconnect()
        if HEROKU_APP is not None:
            HEROKU_APP.restart()


@catub.cat_cmd(
    pattern=r"update(| now)?$",
    command=("update", plugin_category),
    info={
        "header": "To update userbot.",
        "description": "I recommend you to do update deploy atlest once a week.",
        "options": {
            "now": "Will update bot but requirements doesnt update.",
            "deploy": "Bot will update completly with requirements also.",
        },
        "usage": [
            "{tr}update",
            "{tr}update now",
            "{tr}update deploy",
        ],
    },
)
async def upstream(event):
    "To check if the bot is up to date and update if specified"
    conf = event.pattern_match.group(1).strip()
    event = await edit_or_reply(event, "`Checking for updates, please wait....`")
    off_repo = UPSTREAM_REPO_URL
    force_update = False
    if ENV and (HEROKU_API_KEY is None or HEROKU_APP_NAME is None):
        return await edit_or_reply(event, "`Set the required vars first to update the bot`")
    try:
        txt = "`Oops.. Updater cannot continue due to " + "some problems occured`\n\n**LOGTRACE:**\n"

        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f"{txt}\n`directory {error} is not found`")
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f"{txt}\n`Early failure! {error}`")
        return repo.__del__()
    except InvalidGitRepositoryError as error:
        if conf is None:
            return await event.edit(f"`Unfortunately, the directory {error} does not seem to be a git repository.\nBut we can fix that by force updating the userbot using .update now.`")

        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        force_update = True
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    ac_br = repo.active_branch.name
    if ac_br != UPSTREAM_REPO_BRANCH:
        await event.edit("**[UPDATER]:**\n" f"`Looks like you are using your own custom branch ({ac_br}). " "in that case, Updater is unable to identify " "which branch is to be merged. " "please checkout to any official branch`")
        return repo.__del__()
    with contextlib.suppress(BaseException):
        repo.create_remote("upstream", off_repo)
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    # Special case for deploy
    if changelog == "" and not force_update:
        await event.edit("\n`CATUSERBOT is`  **up-to-date**  `with`  " f"**{UPSTREAM_REPO_BRANCH}**\n")
        return repo.__del__()
    if conf == "" and not force_update:
        await print_changelogs(event, ac_br, changelog)
        await event.delete()
        return await event.respond(f"do `{cmdhd}update deploy` to update the catuserbot")

    if force_update:
        await event.edit("`Force-Syncing to latest stable userbot code, please wait...`")
    if conf == "now":
        await event.edit("`Updating userbot, please wait....`")
        await update_bot(event, repo, ups_rem, ac_br)
    return


@catub.cat_cmd(
    pattern=r"update deploy$",
)
async def update_deploy(event):
    if ENV:
        if HEROKU_API_KEY is None or HEROKU_APP_NAME is None:
            return await edit_or_reply(event, "`Set the required vars first to update the bot`")
    elif os.path.exists("config.py"):
        return await edit_delete(
            event,
            f"I guess you are on selfhost. For self host you need to use `{cmdhd}update now`",
        )
    event = await edit_or_reply(event, "`Pulling the nekopack repo wait a sec ....`")
    off_repo = "https://github.com/TgCatUB/nekopack"
    os.chdir("/app")
    try:
        txt = "`Oops.. Updater cannot continue due to " + "some problems occured`\n\n**LOGTRACE:**\n"

        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f"{txt}\n`directory {error} is not found`")
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f"{txt}\n`Early failure! {error}`")
        return repo.__del__()
    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    with contextlib.suppress(BaseException):
        repo.create_remote("upstream", off_repo)
    ac_br = repo.active_branch.name
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    await event.edit("`Deploying userbot, please wait....`")
    await deploy(event, repo, ups_rem, ac_br, txt)


@catub.cat_cmd(
    pattern=r"(good|bad)cat$",
    command=("switch", plugin_category),
    info={
        "header": "To switch between goodcat & badcat(For extra nsfw and gali).",
        "usage": [
            "{tr}goodcat",
            "{tr}badcat",
        ],
    },
)
async def variable(event):  # sourcery skip: low-code-quality
    "To switch between good & bad cat"
    switch = "BADCAT"
    config = "config.py"
    cmd = event.pattern_match.group(1).lower()
    if ENV:
        if (HEROKU_APP_NAME is None) or (HEROKU_API_KEY is None):
            return await edit_delete(
                event,
                "Set the required vars in heroku to function this normally `HEROKU_API_KEY` and `HEROKU_APP_NAME`.",
            )
        app = Heroku.app(Config.HEROKU_APP_NAME)
        heroku_var = app.config()
        if cmd == "good":
            if BADCAT:
                await edit_or_reply(event, "`Changing badcat to goodcat wait for 2-3 minutes.`")
                del heroku_var[switch]
                return
            await edit_delete(event, "`You already using GoodCat`", 6)
        else:
            if BADCAT:
                return await edit_delete(event, "`You already using BadCat`", 6)
            await edit_or_reply(event, "`Changing goodcat to badcat wait for 2-3 minutes.`")
            heroku_var[switch] = "True"
    elif os.path.exists(config):
        string = ""
        match = None
        with open(config, "r") as f:
            configs = f.readlines()
        for i in configs:
            if switch in i:
                match = True
            else:
                string += f"{i}"
        if cmd == "good":
            if match and not BADCAT:
                cat = await edit_or_reply(event, "`Changing badcat to goodcat wait for 2-3 minutes.`")
                with open(config, "w") as f1:
                    f1.write(string)
                    f1.close()
                await _catutils.runcmd("rm -rf badcatext")
                return await event.client.reload(cat)
            await edit_delete(event, "`You already using GoodCat`")
        elif cmd == "bad":
            if match and BADCAT:
                return await edit_or_reply(event, "`You already using BadCat`")
            string += f'    {switch} = "True"\n'
            cat = await edit_or_reply(event, "`Changing goodcat to badcat wait for 2-3 minutes.`")
            with open(config, "w") as f1:
                f1.write(string)
                f1.close()
            await event.client.reload(cat)
    else:
        await edit_delete(event, "`There no Config file , You can't use this plugin.`")
