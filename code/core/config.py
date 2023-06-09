import os
import yaml
import logging

from EdgeGPT import ConversationStyle
from larksuiteoapi import Config, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG
from larksuiteoapi.service.im.v1 import Service as ImService


def load_global_config(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            config = yaml.safe_load(f)
    else:
        config = dict()
        config["APP_ID"] = os.environ.get("APP_ID")
        config["APP_SECRET"] = os.environ.get("APP_SECRET")
        config["APP_VERIFICATION_TOKEN"] = os.environ.get("APP_VERIFICATION_TOKEN")
        config["APP_ENCRYPT_KEY"] = os.environ.get("APP_ENCRYPT_KEY")
        # Note(liyurui): the bot name must equal to the bot name in feishu
        config["BOT_NAME"] = os.environ.get("BOT_NAME", "")
        config["CERT_FILE"] = "cert.pem"
        config["KEY_FILE"] = "key.pem"
        config["COOKIE_URL"] = os.environ.get("COOKIE_URL", "")
        config["CONVERSATION_STYLE"] = "balanced"
    config["CONVERSATION_STYLE"] = ConversationStyle[config["CONVERSATION_STYLE"]]

    return config


global_config = load_global_config("config.yaml")


def _get_sdk_config():
    app_settings = Config.new_internal_app_settings(
        app_id=global_config["APP_ID"],
        app_secret=global_config["APP_SECRET"],
        verification_token=global_config["APP_VERIFICATION_TOKEN"],
        encrypt_key=global_config["APP_ENCRYPT_KEY"],
    )
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    # TODO: log level use config file
    sdk_config = Config.new_config_with_memory_store(
        DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG
    )
    return sdk_config


sdk_config = _get_sdk_config()
service = ImService(sdk_config)
