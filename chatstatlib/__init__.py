import os
from os.path import isfile, isdir

from . import irssi
from . import weechat
from .counters import counters, counterToRank
from .parser import parseFile
from .unpackjson import unpackJSON
from .util import findFiles, rankToFile, rankToJSON

formats = {
    'irssi': irssi,
    'weechat': weechat
    }

