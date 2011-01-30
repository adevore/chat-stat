import functools, itertools, os
from os.path import exists, isfile, isdir

def parseLineCallback(func):
    """
    Create a parseLine callback from a generator
    """
    @functools.wraps(func)
    def factory(*args, **kwargs):
        generator = func(*args, **kwargs)
        generator.next()
        return generator.send
    return factory


def rankToFile(fp, rank):
    for i, (nick, count) in zip(itertools.count(1), rank):
        if isinstance(count, (int, long)):
            s = "{0} {1} {2}\n".format(i, nick, count)
        else:
            s = "{0} {1} {2:.4}\n".format(i, nick, count)
        fp.write(s)

def findFiles(sources, regexp=None):
    result = set()
    for source in sources:
        source = os.path.abspath(os.path.expanduser(source))
        if not exists(source):
            print "file path {0} does not exist".format(source)
            exit(1)
        elif isfile(source):
            result.add(source)
        elif isdir(source):
            for dirpath, dirnames, filenames in os.walk(source):
                for filename in filenames:
                    if not regexp or regexp.match(filename):
                        result.add(os.path.join(dirpath, filename))
    return result
