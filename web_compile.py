import optparse
import os
import sys
from os.path import dirname, expanduser, exists, abspath

import jinja2

from jinja2 import Environment, PackageLoader, Template

from chatstatlib import unpackJSON

TEMPLATE_NAME = "index-template.html"

USAGE = "%prog [options] <target config> <stats config>"
options = optparse.OptionParser(usage=USAGE)


def checkPaths(target, stats, outfile):
    if not exists(target):
        print "Config for targets '%s' does not exist" % target
        exit(1)
    elif not exists(stats):
        print "Config for stats '%s' does not exist" % stats
        exit(1)
    elif outfile:
        outdir = dirname(abspath(expanduser(outfile)))
        if not exists(outdir):
            print "directory for out file '%s' does not exist" % outfile


def compileTemplate(tree):
    # TODO Set up PackageLoader
    loader = PackageLoader('chatstatlib', 'templates')
    env = Environment(loader=loader)

    template = env.get_template(TEMPLATE_NAME)
    return template.render(channels=tree.channels, stats=tree.stats)


def channelSortKey(channel):
    label = channel.label
    # Sort ##foo channels as if they're #foo
    if label.startswith("#"):
        return "#" + label.lstrip("#")
    else:
        return label


def main():
    opts, args = options.parse_args()
    if len(args) not in (2, 3):
        options.print_help()
        exit(1)
    targetConfigPath = expanduser(args[0])
    statsConfigPath = expanduser(args[1])
    if len(args) == 3:
        outfile = args[2]
    else:
        outfile = None
    checkPaths(targetConfigPath, statsConfigPath, outfile)
    if outfile:
        out = open(outfile, 'w')
        os.chmod(outfile, 0755)
    else:
        out = sys.stdout
    tree = unpackJSON(targetConfigPath, statsConfigPath)
    if tree.sort:
        tree.channels.sort(key=channelSortKey)
    html = compileTemplate(tree)
    out.write(html)

if __name__ == "__main__":
    main()
