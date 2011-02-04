# weechat.py: Weechat support

import re
import time
from itertools import count

from . import util, unpackjson

ENCODING = None

LOG_FILE_NAME_RE = re.compile(r"irc.(?P<net>[^.]+)\.(?P<chan>[^.]+).weechatlog")
PERMISSIONS_SYMBOLS = "+@%"  # argument to str.strip is a string

TIMESTAMP_RE = r"(?P<time>[^\t]+)"
LINE_RE = re.compile(TIMESTAMP_RE + r"\t(?P<subject>[^\t]*)\t(?P<msg>.+)")

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
PATH_FORMAT = "irc.{network}.{channel}.weechatlog"

@util.parseLineCallback
def lineParser():
    messageData = None
    for lineno in count(1):
        line = yield messageData

        match = LINE_RE.match(line)
        if not match:
            print [ord(c) for c in line]
            raise Exception(u"invalid line {0}".format(lineno))
            raise Exception(u"invalid line {0}: {1}".format(lineno, line))

        t = match.group("time")
        time_struct = time.strptime(t, TIME_FORMAT)
        subject = match.group("subject").strip()
        subject = subject.lstrip(PERMISSIONS_SYMBOLS)
        msg = match.group("msg")
        if subject == "<--":
            nick, _ = msg.split(' ', 1)
            messageData = {
                'time': time_struct,
                'nick': nick,
                'msg': None,
                'type': "part"}
        # /me
        elif subject == "*":
            try:
                split = msg.split(" ", 1)
                nick = split[0]
                if len(split) == 2:
                    msg = split[1]
                else:
                    msg = ""
                messageData = {
                    'time': time_struct,
                    'nick': nick,
                    'msg': msg,
                    'type': 'me'}
            except ValueError:
                print msg
                raise
        elif subject == "-->":
            nick, _ = msg.split(' ', 1)
            messageData = {
                'time': time_struct,
                'nick': nick,
                'msg': None,
                'type': "join"}
        elif subject == "--":
            messageData = None
            continue
        elif subject == "":
            messageData = None
        # regular message
        else:
            nick = subject
            messageData = {
                'time': time_struct,
                'nick': nick,
                'msg': msg,
                'type': 'regular'}


def formatPath(**kwargs):
    if not kwargs.get('network', None):
        raise unpackjson.error("Weechat requires a network")
    PATH_FORMAT.format(**kwargs)


def findChannelFiles(root, channel, network=None):
    return [os.path.join(root, formatPath(channel=channel, network=network))]
