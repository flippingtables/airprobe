#!/usr/bin/env python

import os
from lxml import etree
from optparse import OptionParser

# get GPS data

# read all xml files
#   parse them for interesting items
#   export interesting things to database?
CHANNELS = {}
CELLS = {}

def fileHasContents(fileName):
    size = os.stat(fileName).st_size
    return (size > 306)


def getCells(parent):
    cellElements = parent.xpath('//field/field[@name="gsm_a.bssmap.cell_ci"]')
    print("Cell: %s" % (len(cellElements)))
    cells = []
    for c in cellElements:
        cellId = c.get("show")
        cellDecim = (int(cellId, 16))
        if cellDecim not in cells:
            cells.append(cellDecim)
    return cells


def hexToDecim(hexValue):
    return (int(hexValue, 16))


def getChannel(fileName):
    return fileName.split("chan")[1].split(".")[0]


def getLAI(parent):
    MCC = parent.xpath('//field/field/field[@name="e212.mcc"]/@show')
    MNC = parent.xpath('//field/field/field[@name="e212.mnc"]/@show')
    LAC = parent.xpath('//field/field/field[@name="gsm_a.lac"]/@show')

    MCC = list(set(MCC))
    MNC = list(set(MNC))
    LAC_HEX = list(set(LAC))
    LAC = map(lambda nr : hexToDecim(nr), LAC_HEX)
    #print("MCC %s, MNC %s, LAC %s" % (MCC, MNC, LAC))
    LAI = {}
    LAI["mcc"] = MCC
    LAI["mcn"] = MNC
    LAI["lac"] = LAC
    print(LAI)

def parseFiles(root, files):
    for fileName in files:
        fullpath = root + "/" + fileName
        
        CHANNELS["channel"] = getChannel(fileName)

        if not fileHasContents(fullpath):
            continue

        tree = etree.parse(fullpath)
        #protoElements = tree.xpath('//proto[@name="gsm_a.ccch"]')

        #System Information Type 3
        protoElements = tree.xpath('//proto[@name="gsm_a.ccch"]/field[@value="1b"]')

        print("FileName: %s, %s" % (fileName, len(protoElements)))
        for el in protoElements:
            #Get the parent
            parent = el.getparent()
            
            cells = getCells(parent)
            print(cells)
            getLAI(parent)

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
