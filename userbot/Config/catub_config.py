""" Config values will be loaded from here """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.
# https://github.com/TgCatUB/catuserbot - GNU v3.0 License
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import os

ENV = bool(os.environ.get("ENV", True))  # <- Default True for Koyeb

if ENV:
    from sample_config import Config  # Import from env-compatible config
elif os.path.exists("config.py"):
    from config import Development as Config
else:
    raise Exception("No valid configuration found. Please set ENV=True and use sample_config.py or provide config.py.")
