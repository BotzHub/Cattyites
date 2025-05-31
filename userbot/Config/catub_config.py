""" Config values will be loaded from here """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.
# https://github.com/TgCatUB/catuserbot - GNU v3.0 License
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import os

ENV = bool(os.environ.get("ENV", True))  # Default True for Koyeb/Replit

if ENV:
    from sample_config import Config  # ✅ Uses env vars for Koyeb/Heroku/etc.
elif os.path.exists("config.py"):
    from config import Development as Config  # ✅ For local dev only
else:
    raise Exception(
        "❌ No configuration found. Either set ENV=True or create config.py with Development class."
    )
