import codecs


def parseFile(fileName, lineCallback, statCallbacks, encoding):
    """
    Parses file using generators as coroutines. See PEP 342.

    opts: result from OptionParser.parse_args()[0]
    lineCallback: Callback to parse each line (can be generator.send)
    statCallbacks: list of callbacks if lineCallback != None
    """

    with codecs.open(fileName, encoding=encoding, errors='ignore') as f:
        for line in f:
            line = line.rstrip("\r\n")
            messageData = lineCallback(line)
            if messageData:
                assert 'time' in messageData
                assert 'msg' in messageData
                assert 'nick' in messageData
                for cb in statCallbacks:
                    cb(messageData)
