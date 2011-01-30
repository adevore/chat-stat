import json, os


def assertJSON(node, key=None, type=None):
    assert key or type
    if type:
        if not isinstance(node, type):
            print "node {0} is not a {1}".format(node, type)
            exit(1)
    if key:
        if key not in node:
            print "node {0} does not have child {1}".format(node, key)


def jsonKey(node, key):
    assertJSON(node, key=key)
    return node[key]


class Channel(object):
    def __init__(self, parent, subtree):
        self.limits = parent.defaultLimits
        if 'limits' in subtree:
            self.limits = subtree['limits']
        self.id = jsonKey(subtree, 'id')
        self.label = jsonKey(subtree, 'label')
        self.source = jsonKey(subtree, 'src')


class Statistic(object):
    def __init__(self, parent, subtree):
        self.label = jsonKey(subtree, 'label')
        self.id = jsonKey(subtree, 'id')
        self.counter = jsonKey(subtree, 'counter')
        self.args = subtree.get('args', [])
        self.kwargs = subtree.get('kwargs', {})


class Orders(object):
    def __init__(self, targetJSON, statsJSON):
        self.defaultLimits = targetJSON.get('limits', [0])
        self.format = jsonKey(targetJSON, 'format')
        self.channels = [Channel(self, target)
            for target in jsonKey(targetJSON, 'targets')]
        assertJSON(statsJSON, type=list)
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