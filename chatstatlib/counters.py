# counters for various statistics
# Examples for: generators, coroutines, decorators, sorted

import time
import re
from collections import defaultdict
from functools import partial

# cuss words in a separate file for those with delicate eyes
with open('cuss_words.txt') as f:
    CUSS_WORDS = [line.strip() for line in f]

SHOUT_MINIMUM = 8
EXCLAMATION_MINIMUM = 3
FLAP_MAX_TIME = 60 * 10
WORD_SPLIT_RE = re.compile(r"\w+", re.UNICODE)
DIRECT_MESSAGE_RE = re.compile(r"^(?P<nick>[^:\s]+): (?P<msg>.*)$")
THING_SUBPATTERN = r"(\(([^)]+)\)|[\w]+)"
KARMA_INCREMENT = re.compile(THING_SUBPATTERN + "\+\+")
KARMA_DECREMENT = re.compile(THING_SUBPATTERN + "--")
BOT_RELAY_PATTERN = "{begin}(?P<nick>[^{end}]+){end} (?P<msg>.*)"

def counter(generator):
    """
    Function decorator to create a generator factory wrapper
    around each counter generator
    """
    def factory(*args, **kwargs):
        d = defaultdict(int)
        sink = generator(d, *args, **kwargs)
        sink.next()
        return d, sink.send
    return factory

@counter
def talk(c):
    while True:
        msg = yield
        if msg['type'] in ('regular', 'me'):
            c[msg['nick']] += 1

@counter
def char(c):
    while True:
        msg = yield
        if msg['type'] in ('regular', 'me'):
            c[msg['nick']] += len(msg['msg'])


@counter
def wordFrequency(c, words, multiple=True):
    while True:
        msg = yield
        if msg['type'] in ('regular', 'me'):
            instances = 0
            text = msg['msg']
            for word in words:
                if multiple:
                    instances += text.count(word)
                else:
                    instances = 1 if word in text else 0
            c[msg['nick']] += instances


@counter
def wordCount(c, words=None):
    while True:
        msg = yield
        if msg['type'] in ('regular', 'me'):
            for word in WORD_SPLIT_RE.findall(msg['msg']):
                if not words or word in words:
                    c[word] += 1


@counter
def upperCount(c):
    while True:
        msg = yield
        if msg['type'] in ('regular', 'me'):
            text = msg['msg']
            # strip nicks off of "nick: A message here!"
            match = DIRECT_MESSAGE_RE.match(text)
            if match:
                text = match.group("msg")
            words = WORD_SPLIT_RE.findall(text)
            # Ignore SHOUTING
            if len(words) > 1 and all(word.isupper() for word in words):
                continue
            else:
                for word in words:
                    if len(word) > 1 and word.isupper():
                        c[word] += 1

@counter
def generous(c, name=""):
    name += "++"
    while True:
        msg = yield
        if msg['type'] in ('regular', 'me'):
            c[msg['nick']] += msg['msg'].count(name)


@counter
def hateful(c, name=""):
    name += "--"
    while True:
        msg = yield
        if msg['type'] in ('regular', 'me'):
            c[msg['nick']] += msg['msg'].count(name)


@counter
def regexpCount(c, regexp, caseSensitive=True):
    if not caseSensitive:
        # Map a lower cased match group to the first match group
        # e.g. "minecraft": "Minecraft"
        lowerCaseds = {}
    while True:
        msg = yield
        if msg['type'] in ('regular', 'me'):
            matches = regexp.finditer(msg['msg'])
            for match in matches:
                phrase = match.group(1)
                assert phrase is not None
                if not caseSensitive:
                    lowered = phrase.lower()
                    if lowered in lowerCaseds:
                        c[lowerCaseds[lowered]] += 1
                    else:
                        lowerCaseds[lowered] = phrase
                        c[phrase] += 1
                else:
                    c[phrase] += 1


loved = partial(regexpCount, KARMA_INCREMENT, caseSensitive=False)
hated = partial(regexpCount, KARMA_DECREMENT, caseSensitive=False)


@counter
def joins(c):
    while True:
        msg = yield
        if msg['type'] == 'join':
            c[msg['nick']] += 1


@counter
def shout(c):
    while True:
        msg = yield
        if (msg['type'] == "regular" and
               len(msg['msg']) >= SHOUT_MINIMUM and
                msg['msg'].isupper()):
            c[msg['nick']] += 1


@counter
def flap(c, interval=FLAP_MAX_TIME):
    lastLeave = {}
    while True:
        msg = yield
        if msg['type'] == 'part':
            lastLeave[msg['nick']] = time.mktime(msg['time'])
        elif msg['type'] == 'join':
            now = time.mktime(msg['time'])
            if now - lastLeave.get(msg['nick'], 0) < interval:
                c[msg['nick']] += 1

@counter
def relayCount(c, begin, end, relayer=None,):
    regexp = re.compile(BOT_RELAY_PATTERN.format(begin=begin, end=end))
    while True:
        msg = yield
        if msg['type'] == 'regular' and (relayer is None or msg['nick'] == relayer):
            match = regexp.match(msg['msg'])
            if match:
                c[match.group('nick')] += 1


counters = {
    'talk': talk,
    'char': char,
    'generous': generous,
    'hateful': hateful,
    'cuss': partial(wordFrequency, CUSS_WORDS),
    'cusscount': partial(wordCount, CUSS_WORDS + ["penguin"]),
    'joins': joins,
    'beerfan': partial(generous, name="beer"),
    'exclamation': partial(wordFrequency,
                   ['!' * EXCLAMATION_MINIMUM], multiple=False),
    'shout': shout,
    'flap': flap,
    'wordcount': wordCount,
    'uppercount': upperCount,
    'hated': hated,
    'loved': loved,
    'relaycount': relayCount,
    'smpbotrelay': partial(relayCount, '<', '>', "SMP-Bot"),
    'mcbotrelay': partial(relayCount, '<', '>'),
    }


def counterToRank(d):
    return sorted(d.items(), key=lambda v:v[1], reverse=True)
