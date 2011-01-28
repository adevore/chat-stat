import re
import time
from itertools import count
from . import util

LOG_FILE_NAME_RE = re.compile(r"[^.]+\.log")
LOG_CHANNEL_NAME_RE = re.compile(r"#[^.]+\.log")

OPEN_RE = re.compile(r"^--- Log opened (.*)")
NICK_CHANGE_RE = re.compile(r"\d{2}:\d{2} -!- ([^\s]+) is now known as (.*)$")
USER_MODE_RE = re.compile(r"(?P<time>\d{2}:{2}) -!- mode/(?P<chan>#[^s]+)\[?P<perm>([+-]\w) (?P<nick>\]+]) by (?P<granter>.+)")

IGNORE_RES = [
    re.compile(r"^--- Log closed.*"),
    re.compile(r"\d{2}:\d{2} -[^:]+:#"),
    re.compile(r"\d{2}:\d{2} !.*invited.*$"), # invite to channel
    re.compile(r"^--- Log closed.*"),
    re.compile(r"\d{2}:\d{2} -!- [^\s]+ is now known as"),
    NICK_CHANGE_RE,
    USER_MODE_RE,
    ]

DAY_CHANGE_RE = re.compile(r"--- Day changed (\w{3} \w{3} \d{2} \d{4})")
MESSAGE_RE = re.compile(r"^(?P<time>\d{2}:\d{2}) <[^\w]?(?P<nick>[^>]+)> (?P<msg>.*)$")
ME_RE = re.compile(r"^(?P<time>\d{2}:\d{2})\s+\*\s+(?P<nick>[^\s]*) (?P<msg>.*)$")
JOIN_PART_RE = re.compile(r"(?P<time>\d{2}:\d{2}) -!- (?P<nick>[^\s]+) \[[^\]]+\] has (?P<action>joined|quit)")

LOG_OPEN_TIME = "%a %b %d %H:%M:%S %Y"
DAY_CHANGE_TIME = "%a %b %j %Y"
MESSAGE_TIME = "%H:%M"

def updateHourMinute(then, timestamp):
    """
    strptime has performance issues, so do custom parsing on IRSSI's Hour:Minute format
    """
    hour, minute = timestamp.split(":")
    newTime = list(then)
    newTime[3] = int(hour)
    newTime[4] = int(minute)
    newTime[5] = 0 # tm_sec
    return time.struct_time(newTime)

@util.parseLineCallback
def lineParser():
    currentTime = None
    messageData = None
    for lineno in count(1):
        # yield last messageData, get next line
        # first yield is None because the first line opens the file
        line = yield messageData

        match = MESSAGE_RE.match(line) or ME_RE.match(line)
        if match:
            t = match.group("time")
            nick = match.group("nick")
            msg = match.group("msg")

            currentTime = updateHourMinute(currentTime, t)

            messageData = {
                'time': currentTime,
                'nick': nick,
                'msg': msg,
                'type': "regular"}
            continue

        match = OPEN_RE.match(line)
        if match:
            t = match.group(1)
            currentTime = time.strptime(t, LOG_OPEN_TIME)
            messageData = None
            continue

        match = DAY_CHANGE_RE.match(line)
        if match:
            t = match.group(1)
            currentTime = time.strptime(t, DAY_CHANGE_TIME)
            messageData = None
            continue

        match = JOIN_PART_RE.match(line)
        if match:
            t = match.group(1)
            currentTime = updateHourMinute(currentTime, t)
            if match.group("action") == "joined":
                messageType = "join"
            else:
                messageType = "part"
            messageData = {
                'time': currentTime,
                'nick': match.group("nick"),
                'msg': None,
                'type': messageType}
            continue

        for regexp in IGNORE_RES:
            if regexp.match(line):
                break
        else:
            #raise Exception("Invalid line %i in file: %s" % (lineno, line))
            pass
