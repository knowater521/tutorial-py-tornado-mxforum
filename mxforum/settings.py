#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

import os
from dotenv import load_dotenv
import peewee_async

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

YUNPIAN_APIKEY = os.environ.get("YUNPIAN_APIKEY", None)
YUNPIAN_SIGNATURE = os.environ.get("YUNPIAN_SIGNATURE", None)
TEST_MOBILE = os.environ.get("TEST_MOBILE", None)

settings = {
    "static_search": BASE_DIR,
    "static_url_prefix": "/static",
    "template_path": "templates",
    # custom
    "debug": os.environ.get("DEBUG", "false").lower() in ["true", "on", "1"],
    "secret_key": os.environ.get("SECRET_KEY", "you'll never gue55 it"),
    "media_root": os.path.join(BASE_DIR, "media"),
    "site_url": os.environ.get("SITE_URL", "http://127.0.0.1:8888"),
    "db": {
        "host": "127.0.0.1",
        "user": "mxforum",
        "password": "mxforum",
        "name": "message",
        "port": 3306,
    },
    "redis": {"host": "127.0.0.1", "port": 6379},
}

database = peewee_async.MySQLDatabase(
    "mxforum", host="127.0.0.1", port=3306, user="mxforum", password="mxforum"
)
