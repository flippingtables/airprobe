#!/usr/bin/env python

import os
from lxml import etree
from optparse import OptionParser
import json
from pprint import pprint


# get GPS data

# read all xml files
#   parse them for interesting items
#   export interesting things to database?
SCANS = {}
CHANNELS = {}
CELLS = {}
EVERYTHING = {}


def getGPScoords(root, fileName):
    fp = "%s/%s" % (root, fileName)
    data = []
    with open(fp) as data_file:
        for line in data_file:
            if "lat" in line and "lon" in line and "time" in line:
                data.append(json.loads(line))
                break
    latlon = {}
    latlon["time"]  = (data[0]["time"])
    latlon["lat"] = (data[0]["lat"])
    latlon["lon"] = (data[0]["lon"])
    return latlon


def getTimeFromScan(directory):
    fileDir = directory.rsplit("/")[-2]
    return fileDir


def fileHasContents(fileName):
    size = os.stat(fileName).st_size
    return (size > 306)


def getCells(parent):
    cellElements = parent.xpath('//field/field[@name="gsm_a.bssmap.cell_ci"]')
    cells = []
    for c in cellElements:
        cellId = c.get("show")
        cellDecim = (int(cellId, 16))
        if cellDecim not in cells:
            cells.append(cellDecim)
    return cells


def hexToDecim(hexValue):
    return (int(hexValue, 16))


#filename is: chanNN.cfile.xml
def getChannel(fileName):
    return fileName.split("chan")[1].split(".")[0]


# returns the Location Area Identifier: Mobile Country Code, Mobile Network Code, Location Area Code
def getLAI(parent):
    MCC = parent.xpath('//field/field/field[@name="e212.mcc"]/@show')
    MNC = parent.xpath('//field/field/field[@name="e212.mnc"]/@show')
    LAC = parent.xpath('//field/field/field[@name="gsm_a.lac"]/@show')

    MCC = list(set(MCC))
    MNC = list(set(MNC))
    LAC_HEX = list(set(LAC))
    LAC = map(lambda nr: hexToDecim(nr), LAC_HEX)
    
    LAI = {}
    LAI["mcc"] = MCC
    LAI["mcn"] = MNC
    LAI["lac"] = LAC

    return LAI

def parseFiles(root, files):
    timeFromScan = ""
    if ("pcapxml" in root):
        timeFromScan = getTimeFromScan(root)
        insertToDict(EVERYTHING, timeFromScan, timeFromScan)

    for fileName in files:
        fullpath = root + "/" + fileName
        SCAN = {}

        if not fileHasContents(fullpath):
            continue

        if ".json" in fileName:
            d = EVERYTHING[timeFromScan]
            d["GPS"] = getGPScoords(root, fileName)

        if ".xml" not in fileName:
            continue

        channel = getChannel(fileName)
        SCAN["CHANNEL"] = channel
        tree = etree.parse(fullpath)

        #System Information Type 3
        protoElements = tree.xpath('//proto[@name="gsm_a.ccch"]/field[@value="1b"]')

        #print("FileName: %s, %s" % (fileName, len(protoElements)))
        LAI = []
        CELLS = []
        for el in protoElements:
            #Get the parent
            parent = el.getparent()
            CELLS.append(getCells(parent))
            LAI.append(getLAI(parent))
        insertToDict(SCAN, "LAI", LAI)
        insertToDict(SCAN, "CELLS", CELLS)
        SCANS[channel] = SCAN

    EVERYTHING[timeFromScan] = SCANS


def insertToDict(dict, KEY, items):
    if KEY not in dict.keys():
        dict[KEY] = items
    else:
        d = dict[KEY]
        d.append(items)
    return dict


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


def dump(theThing):
    with open('DUMP.txt', 'w') as the_file:
        #the_file.write(theThing)
        pprint(theThing, stream=the_file)


def doit(directory, levels):
    for root, dirs, files in walklevel(directory, levels):
        parseFiles(root, files)

    dump(EVERYTHING)
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
                      default=3,
                      help="Number of levels deep you want traverse in the directory",)
    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("wrong number of arguments")
    doit(options.directory, options.levels)


if __name__ == '__main__':
    main()
