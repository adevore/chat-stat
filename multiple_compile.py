import optparse
from os.path import isdir
from chatstatlib import unpackJSON


USAGE = "%prog [options] <target json> <stats config> <destination>"

options = optparse.Options()
options.add_option("-v", "--verbose", action="store_true",
    dest="verbose", default=False, help="verbose output")


def checkPaths(targetConfig, statsConfig, dest):
    for fileName in (targetConfig, statsConfig, dest):
        if not exists(fileName):
            print "file/directory %s does not exist"
            exit(1)

    if not isdir(destDir):
        print "destination %s is not a directory"
        exit(1)


def compileTarget(config, target):


def main():
    opts, args = options.parse_args()
    if len(args) != 3:
        options.print_usage()
        exit(1)

    targetConfigFile = args[0]
    statsConfigFile = args[1]
    destDir = args[2]

    config = unpackJSON(targetConfigFile, statsConfigFile)
    for target in config.targets:
        compileTarget(config, target)