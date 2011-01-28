import optparse
import os
import sys
import time
import itertools

import chatstatlib

USAGE = "%prog [options] FILE..."

options = optparse.OptionParser(usage=USAGE)
options.add_option("-v", "--verbose", action="store_true",
    dest="verbose", default=False, help="verbose output")
options.add_option("-c", "--channels-only", action="store_true",
    dest="channelsOnly", default=False,
    help="only find channels when searching for files")
options.add_option("-s", "--stat", dest="stat", default="talk",
    help="type of stat to output")
options.add_option("-l", "--limit", dest="limit", default=0, type="int",
    help="Limit to how many people to show (0 for all)")
options.add_option("-f", "--format", dest="format", default="irssi",
    help="Log file format")
options.add_option("-o", "--out", dest="out", default="-",
    help="Output file (- for stdout)")
options.add_option("--list-stats", dest="listStats", action="store_true",
    help="List all statistics analyzers and exit")


def main():
    opts, args = options.parse_args()
    if opts.listStats:
        for name in sorted(chatstatlib.counters):
            print name
        return 0
    if not args:
        print "No file names given!"
        return 1
    if opts.format not in chatstatlib.formats:
        print "unimplemented log format", opts.format
        return 1
    if opts.stat not in chatstatlib.counters:
        print "unimplemented stat type", opts.stat
        return 1
    if opts.out == '-':
        outfile = sys.stdout
    else:
        outfile = open(os.path.expanduser(opts.out), 'w')

    # Choose log file format (irssi, weechat, bip, etc.)
    formatModule = chatstatlib.formats[opts.format]

    # Choose a search regexp based on --channel
    if opts.channelsOnly:
        fregexp = formatModule.LOG_CHANNEL_NAME_RE
    else:
        fregexp = formatModule.LOG_FILE_NAME_RE
    fileNames = sorted(chatstatlib.findFiles(args, fregexp))
    if not fileNames:
        print "no log files found"
        return 1

    lineParserGen = formatModule.lineParser # one generator per file
    counter, sink = chatstatlib.counters[opts.stat]()
    messageCallbacks = [sink]
    for fileName in fileNames:
        if opts.verbose:
            print "processing", fileName,
            start = time.time()
        lineParser = formatModule.lineParser()
        chatstatlib.parseFile(fileName, lineParser, messageCallbacks)
        if opts.verbose:
            print "(%.4f seconds)" % (time.time() - start)

    rank = chatstatlib.counterToRank(counter)
    if opts.limit:
        iterable = itertools.islice(rank, opts.limit)
    else:
        iterable = rank

    print >> outfile, "rank nick count"
    for i, (nick, count) in zip(itertools.count(1), iterable):
        print >> outfile, i, nick, count

if __name__ == "__main__":
    exit(main())
