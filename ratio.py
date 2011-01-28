import optparse, sys, itertools
from chatstatlib import counterToRank
from chatstatlib.util import rankToFile


options = optparse.OptionParser()
options.add_option("-o", "--outfile", dest="outfile", default="-",
                   help="Output file (defaults to stdin)")


def main():
    opts, args = options.parse_args()
    denominatorFile = args[0]
    numeratorFile = args[1]
    outFile = opts.outfile

    denominators = {}
    numerators = {}
    ratios = {}

    with open(denominatorFile) as df:
        df.next() # Get rid of header
        for line in df:
            line = line.rstrip("\r\n")
            rank, name, count = line.split(' ')
            denominators[name] = int(count)
    with open(numeratorFile) as nf:
        nf.next() # Get rid of header
        for line in nf:
            line = line.rstrip("\r\n")
            rank, name, count = line.split(' ')
            numerators[name] = float(count)
    for name, count in denominators.items():
        if name in numerators:
            ratios[name] = numerators[name] / count

    rankings = counterToRank(ratios)
    if outFile == "-":
        rankToFile(sys.stdout, rankings)
    else:
        with open(outFile) as out:
            rankToFile(out, rankings)


if __name__ == '__main__':
    main()
