"""Config values will be loaded from here"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.
# https://github.com/TgCatUB/catuserbot - GNU v3.0 License
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import os

ENV = bool(os.environ.get("ENV", True))

if ENV:
    from sample_config import Config
elif os.path.exists("config.py"):
    from config import Development as Config
else:
    raise Exception("No valid config found!")
