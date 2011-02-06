import json
import os

from .counters import counters


class FormatError(Exception):
    pass


def assertJSON(node, key=None, type=None):
    assert key or type
    if type:
        if not isinstance(node, type):
            raise FormatError("node {0} is not a '{1}'".format(node, type.__name__))
            exit(1)
    if key and key not in node:
        raise FormatError("node {0} does not have child {1}".format(node, key))


def jsonKey(node, key, type=None, default=None):
    if key not in node:
        if default is not None:
            return default
        else:
            raise FormatError("node {0} does not have child {1}".format(node, key))
    value = node[key]
    if type and not isinstance(value, type):
        raise FormatError("node {0} of type '{1}' is not a '{2}'".format(value, value.__class__.__name__, type.__name__))
    return value


class Channel(object):
    """
    Channel target information
    """

    def __init__(self, parent, subtree):
        self.id = jsonKey(subtree, 'id', type=basestring)
        self.label = jsonKey(subtree, 'label', type=basestring)
        self.source = jsonKey(subtree, 'src', default="", type=basestring)
        self.network = jsonKey(subtree, 'network',
                       default=parent.network, type=basestring)


class Statistic(object):
    def __init__(self, parent, subtree):
        self.limits = jsonKey(subtree, 'limits',
                      default=parent.defaultLimits, type=list)
        self.label = jsonKey(subtree, 'label', type=basestring)
        self.id = jsonKey(subtree, 'id', type=basestring)
        self.counter = jsonKey(subtree, 'counter', type=basestring)
        self.args = jsonKey(subtree, 'args', default=[], type=list)
        self.kwargs = jsonKey(subtree, 'kwargs', default={}, type=dict)

        if self.counter not in counters:
            raise FormatError("counter {0} does not exist".format(self.counter))

    def new(self):
        return counters[self.counter](*self.args, **self.kwargs)


class Orders(object):
    def __init__(self, targetJSON, statsJSON):
        assertJSON(statsJSON, type=list)
        assertJSON(targetJSON, type=dict)
        self.defaultLimits = jsonKey(targetJSON, 'limits',
                             default=[0], type=list)
        self.format = jsonKey(targetJSON, 'format', type=basestring)
        self.network = jsonKey(targetJSON, 'network',
                       default=None, type=basestring)
        self.sort = jsonKey(targetJSON, 'sort', type=bool, default=False)
        self.channels = [Channel(self, target)
            for target in jsonKey(targetJSON, 'targets', type=list)]

        self.stats = [Statistic(self, stat) for stat in statsJSON]


def unpackJSON(targetPath, statsPath):
    """
    Parses JSON, combines it into an object
    """
    with open(os.path.expanduser(targetPath)) as f:
        targetJSON = json.load(f)

    with open(os.path.expanduser(statsPath)) as f:
        statsJSON = json.load(f)

    return Orders(targetJSON, statsJSON)
