import optparse
import codecs
import os
import time
from os.path import isdir, abspath, expanduser, exists

from chatstatlib import unpackJSON, counterToRank, rankToFile, rankToJSON
import chatstatlib


USAGE = "%prog [options] <target json> <stats config> <source> <destination>"
TARGET_LIMIT_FORMAT = "{channel}-{stat}-top{limit}.{ext}"
TARGET_ALL_FORMAT = "{channel}-{stat}-all.{ext}"

options = optparse.OptionParser(usage=USAGE)
options.add_option("-v", "--verbose", action="store_true",
    dest="verbose", default=False, help="verbose output")


def checkPaths(targetConfig, statsConfig, src, dest):
    for fileName in (targetConfig, statsConfig, src, dest):
        if not exists(fileName):
            print "file/directory %s does not exist"
            exit(1)

    if not isdir(dest):
        print "destination %s is not a directory"
        exit(1)


def formatDestination(destDir, target, stat, ext, limit=0):
    formatting = {'channel': target.id, 'stat': stat.id,
                  'limit': limit, 'ext':ext}
    if limit == 0:
        fileName = TARGET_ALL_FORMAT.format(**formatting)
    else:
        fileName = TARGET_LIMIT_FORMAT.format(**formatting)
    return os.path.join(destDir, fileName)

def parseFiles(tree, channel, srcDir, verbose):
    callbacks = []
    counters = []
    formatModule = chatstatlib.formats[tree.format]
    for stat in tree.stats:
        counter, callback = stat.new()
        counters.append((stat, counter))
        callbacks.append(callback)

    files = formatModule.findChannelFiles(srcDir,
        network=channel.network, channel=channel.source)
    for fileName in files:
        if verbose:
            print "parsing", fileName,
            start = time.time()
        lineParser = formatModule.lineParser()
        chatstatlib.parseFile(fileName, lineParser, callbacks)
        if verbose:
            print "({0} seconds)".format(time.time() - start)
    return counters


def writeTarget(destDir, target, counters):
    for stat, counter in counters:
        ranked = counterToRank(counter)
        for limit in stat.limits:
            if limit == 0:
                flatName = formatDestination(destDir, target, stat, "txt")
                jsonName = formatDestination(destDir, target, stat, "json")
                segment = ranked
            else:
                flatName = formatDestination(destDir, target, stat, "txt", limit=limit)
                jsonName = formatDestination(destDir, target, stat, "json", limit=limit)
                segment = ranked[:limit]
            with codecs.open(flatName, 'w', 'utf8', 'replace') as f:
                os.chmod(flatName, 0755)
                rankToFile(f, segment)
            with codecs.open(jsonName, 'w', 'utf8', 'replace') as f:
                os.chmod(jsonName, 0755)
                rankToJSON(f, segment)

def main():
    opts, args = options.parse_args()
    if len(args) != 4:
        options.print_usage()
        exit(1)

    targetConfigFile = abspath(expanduser(args[0]))
    statsConfigFile = abspath(expanduser(args[1]))
    srcDir = abspath(expanduser(args[2]))
    destDir = abspath(expanduser(args[3]))
    checkPaths(targetConfigFile, statsConfigFile, srcDir, destDir)

    config = unpackJSON(targetConfigFile, statsConfigFile)
    for channel in config.channels:
        if opts.verbose:
            print "processing", channel.id,
            start = time.time()
        counters = parseFiles(config, channel, srcDir, opts.verbose)
        writeTarget(destDir, channel, counters)
        if opts.verbose:
            print "({0:.4} seconds)".format(time.time() - start)

if __name__ == '__main__':
    main()