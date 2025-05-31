"""Config values will be loaded from here"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# CatUserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Copyright (C) 2020-2023 by TgCatUB@Github.
# https://github.com/TgCatUB/catuserbot - GNU v3.0 License
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import os

ENV = bool(os.environ.get("ENV", True))

if ENV:
    pass
elif os.path.exists("config.py"):
    pass
else:
    raise Exception("No valid config found!")
