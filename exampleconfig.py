from sample_config import Config


class Development(Config):
    # get this values from the my.telegram.org
    APP_ID = 6
    API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
    # the name to display in your alive message
    ALIVE_NAME = "Your value"
    # create any PostgreSQL database (i recommend to use elephantsql) and paste that link here
    DB_URI = "Your value"
    # After cloning the repo and installing requirements do python3 stringsetup.py an fill that value with this
    STRING_SESSION = "Your value"
    # create a new bot in @botfather and fill the following vales with bottoken
    TG_BOT_TOKEN = "Your value"
    # command handler
    COMMAND_HAND_LER = "."
    # command hanler for sudo
    SUDO_COMMAND_HAND_LER = "."
    # External plugins repo
    EXTERNAL_REPO = "https://github.com/TgCatUB/CatPlugins"
    # if you need badcat plugins set "True"
    BADCAT = "False"
    # set path of the brwoser (Chrome/Chromium) binary , default set to chromium path change it if you are using chrome
    # https://docs.catuserbot.co/catuserbot/installation/guide/chromium-and-chrome-driver-setup
    CHROME_BIN = "/usr/bin/chromium"
