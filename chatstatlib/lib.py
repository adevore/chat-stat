# Copyright (c) 2011 Aaron DeVore
# Released under the MIT License
# Part of IRC Log Stats
#
# Take in directories and files from chat logs, spit out stats
# See --help


import os, sys
from os.path import isfile, isdir, basename, exists
import re
import codecs
from collections import defaultdict
from itertools import count
import time


class error(Exception):
    pass


def findFiles(sources, regexp=None):
    result = set()
    for source in sources:
        source = os.path.abspath(os.path.expanduser(source))
        if isfile(source):
            result.add(source)
        elif isdir(source):
            for dirpath, dirnames, filenames in os.walk(source):
                for filename in filenames:
                    if not regexp or regexp.match(filename):
                        result.add(os.path.join(dirpath, filename))
    return result


lineParsers = {
    'irssi': irssiLineParser,
    #'weechat': weechatLineParser,
    }



if __name__ == '__main__':
    main()
