#!/usr/bin/env python

import os
from lxml import etree
from optparse import OptionParser

# get GPS data

# read all xml files
#   parse them for interesting items
#   export interesting things to database?


def fileHasContents(fileName):
    size = os.stat(fileName).st_size
    return (size > 306)


def parseFiles(root, files):
    for fileName in files:
        fullpath = root + "/" + fileName
        
        if not fileHasContents(fullpath):
            continue

        tree = etree.parse(fullpath)
        protos = tree.xpath('//proto[@name="gsm_a.ccch"]')

        print ("FileName: %s, %s" % (fileName, len(protos)))



def getTreeFromXml(file):
    return etree.parse(file)


def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def doit(directory, levels):
    for root, dirs, files in walklevel(directory, levels):
        print(root)
        print(files)
        parseFiles(root, files)

    print("Done")


def main():
    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 1.0")
    parser.add_option("-d", "--dir",
                            action="store",
                            dest="directory",
                            help="Directory of files you want to process")
    parser.add_option("-l", "--level",
                      action="store",
                      dest="levels",
                      default=1,
                      help="Number of levels deep you want traverse in the directory",)
    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("wrong number of arguments")
    doit(options.directory, options.levels)


if __name__ == '__main__':
    main()
