import json
import os
import sys
import re
import signal
import logging
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

import telebot
from yt_dlp import YoutubeDL, utils

logging.basicConfig(format="%(levelname)s:%(module)s: %(message)s")
logger = logging.getLogger(__name__)
DEBUG = "--debug" in sys.argv
logger.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

load_dotenv()

token = os.environ.get('TOKEN', None)
if not token:
    logger.error("ERROR: Specify TOKEN in an .env file or an environment variable!")
    exit(1)

regex = os.environ.get('REGEX', r'\\bhttps?://\\S+\\b')
tempdir = os.environ.get('TEMPLDIR', '/tmp/ytdlp-telebot')

import shutil
NODE_PATH = shutil.which("node") or "/usr/bin/node"
logger.info(f"Detected Node.js path: {NODE_PATH}")

default_formats = (
    '(ba[ext=m4a] / ba) '
    ' + bv[width>=800][height<=800][filesize<50M]'
    '/(ba[ext=m4a] / ba)'
    ' + bv[width>=800][height>=800][filesize<50M]'
    '/'
    'best[width>=800][height<=800][filesize<50M]'
    '/'
    'best[width>=800][height>=800][filesize<50M]'
    '/'
    '(ba[ext=m4a] / ba)'
    ' + bv[width<=800][filesize<50M]'
    '/'
    'best[width<=800][filesize<50M]'
    '/'
    'bv[filesize<50M] + ba/best[filesize<50M]'
    '/'
    'best'
)

default_sizeless_formats = (
    'ba[ext=m4a] / ba'
    ' + bv[width>=800][height<=800]'
    '/(ba[ext=m4a] / ba)'
    ' + bv[width>=800][height>=800]'
    '/'
    'best[width>=800][height<=800]'
    '/'
    'best[width>=800][height>=800]'
    '/'
    '(ba[ext=m4a] / ba)'
    ' + bv[width<=800]'
    '/'
    'best[width<=800]'
    '/'
    'bv + ba/best'
    '/'
    'best'
)
