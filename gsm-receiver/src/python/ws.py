#!/usr/bin/env python
import os
import time
import subprocess
from optparse import OptionParser


def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def checkIfDirExistsCreateIfNot(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def tshark(root, fileName):
    dest = checkIfDirExistsCreateIfNot(root+"/pcapxml/")
    print("Starting tshark")
    script = "tshark -i lo -f 'udp port 4729' -Y 'gsmtap' -a duration:4 -T pdml > %s%s.xml" % (dest, fileName)
    p = subprocess.Popen(script, shell=True)
    #sleep, otherwise airprobe might be finished before we have initialized properly
    time.sleep(1)
    return p


def runScript(script):
    os.system(script)


def gsmReceive(root, fileName):
    print("Sending with airprobe file: %s/%s" % (root, fileName))
    fullpath = os.path.join(root, fileName)
    quiet = "> /dev/null 2> /dev/null"
    shellscript = "./gsm_receive.py -I %s -d 64 -c 0C %s" % (fullpath, quiet)
    runScript(shellscript)


def handleFiles(root, files):
    for f in files:
        if ".json" in f:
            continue
        p = tshark(root, f)
        gsmReceive(root, f)
        while p.poll() is None:
            time.sleep(1)


def doit(directory, levels):
    for root, dirs, files in walklevel(directory, levels):
        print(root)
        print(files)

        handleFiles(root, files)
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
