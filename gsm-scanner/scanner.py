#!/usr/bin/env python

import os
import time
import sys
from optparse import OptionParser
import shutil

for extdir in ['/home/openbts/Downloads/OSMO/airprobe/gsm-tvoid/src/lib',
               '/home/openbts/Downloads/OSMO/airprobe/gsm-tvoid/src/lib/.libs']:  # '/home/openbts/Downloads/OSMO/airprobe/gsm-tvoid/src/lib']:
    if extdir not in sys.path:
        print("Adding:" + extdir + " to path")
        sys.path.append(extdir)

# GLOBALS
DURATION = 3.5  # number in seconds
# DECIM=64	#decimation
DECIM = 112  #USRP2=174, USRP1=112, or 64
GAIN = 52  #antenna gain
#SAMPLES = 64000000 / DECIM * DURATION


#samples = 10000000

sleepTime = 1
ARFCN_FROM = 1
ARFCN_TO = 124

root = ""


def parse_options():
    parser = OptionParser()

    parser.add_option("-l", "--loop", dest="loop", default=1, type="int",
                      help="Set this flag if you want to loop the ARFCNs N times")
    parser.add_option("-f", "--arfcnfrom", dest="arfcnFROM", default="1", type="int",
                      help="ARFCN Channel to scan from")
    parser.add_option("-t", "--arfcnto", dest="arfcnTO", default="124", type="int",
                      help="ARFCN Channel to scan to")
    parser.add_option("-q", "--quiet",
                      help="Set this flag if you want minimal output to the terminal")
    parser.add_option("-d", "--decim", dest="decim", default="64", type="int",
                      help="Decimation")
    parser.add_option("-x", "--decode", dest="decode", help="Set this flag if you want to decode")

    (options, args) = parser.parse_args()
    if (len(args) != 0):
        parser.print_help()
        sys.exit(1)

    return options


def checkIfDirExistsCreateIfNot(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def getRootDir():
    root = os.path.dirname(os.path.realpath(__file__))
    return root


# get the current directory
def getDir():
    #pwd = os.path.dirname(os.path.realpath(__file__))
    pwd = "/home/openbts/scans"
    currentDateTime = time.strftime("%Y%m%d-%H%M")
    directory = pwd + "/" + currentDateTime + "/"
    # Just to be sure, we will create the directory first
    checkIfDirExistsCreateIfNot(directory)
    return directory


# calculate the frequency of an ARFCN
def calculateFrequency(arfcn):
    return (890.0e6 + (0.2e6 * arfcn) + 45.0e6)


directory = getDir()
# destination = directory + "DST/"
# checkIfDirExistsCreateIfNot(destination)


def runscript(script):
    #print("Running: "+script)
    os.system(script)


def sendToGSMScanLight(options, filename):
    quiet = "> /dev/null 2> /dev/null"
    if (not options.quiet):
        quiet = ""
    script = "python ../gsm-tvoid/src/python/gsm_scan_light.py -SN -pd -d %s -I %s %s" % (
        options.decim, filename, quiet)
    runscript(script)


def havePcapFiles():
    return os.path.isfile("tvoid.pcap") and os.path.isfile("tvoid-burst.pcap")


def checkFileSizeGreaterThan24():
    size = os.stat("tvoid.pcap").st_size
    return (size > 24)


def sendToGsmdecode(channel):
    if havePcapFiles() and checkFileSizeGreaterThan24():
        print("Found something on channel: %s" % channel)
        currentDateTime = time.strftime("%Y%m%d-%H%M")
        filename = destination + str(channel) + "-" + currentDateTime
        shutil.move("tvoid.pcap", filename + ".pcap")
        shutil.move("tvoid-burst.pcap", filename + "-burst.pcap")
        script = "python pcap4gsmdecode.py %s.pcap | ../gsmdecode/src/gsmdecode -i | python analyse.py -a %s" % (
            filename, channel)
        runscript(script)


def gsm900(options):
    SAMPLES = 30000000 / options.decim * DURATION

    quiet = "> /dev/null 2> /dev/null"
    if not options.quiet:
        quiet = ""

    print("Start scan all GSM900")
    for channel in range(options.arfcnFROM, options.arfcnTO):
        frequency = calculateFrequency(channel)

        filename = "%schan%s.cfile" % (directory, channel)
        shellscript = "uhd_rx_cfile.py -A TX/RX -g %s -f %s %s -N %s %s" % (GAIN, frequency, filename, SAMPLES, quiet)

        print("Scanning %s: %s, output to %s") % (channel, frequency, filename)
        #print(shellscript + "\n")
        time.sleep(sleepTime)
        runscript(shellscript)
        if options.decode:
            sendToGSMScanLight(options, filename)

            time.sleep(sleepTime)
            sendToGsmdecode(channel)


        #print("Sending to Wireshark")
        #print(shellscript + "\n")
        #time.sleep(sleepTime)
        #runscript(shellscript)

        #print("Deleting file: %s" % (filename))
        #shellscript = "rm %s" % filename
        #runscript(shellscript)


def walkAllScannedFiles():
    print("Walking all directories")
    for root, _, files in os.walk(directory):
        for f in files:
            fullpath = os.path.join(root, f)
            shellscript = "./gsm_receive.py -I %s -d 64" % (fullpath)
            print shellscript
            os.system(shellscript)
    print("Walking done")


def doSudoSetup():
    os.system("sudo sysctl -w net.core.rmem_max=50000000")
    os.system("sudo sysctl -w net.core.wmem_max=1048576")
    #os.system("sudo ifconfig eth0 192.168.10.1")


def main():
    root = getRootDir()
    doSudoSetup()
    # get parameter
    options = parse_options()

    # check options
    # wrong usage
    if not (options.loop):
        print "We won't loop"
    #sys.exit(1)

    after = 0
    before = 0

    before = before + time.time()
    # correct usage
    if (options.loop):
        for i in range(options.loop):
            gsm900(options)

    after = after + time.time()
    
    #get some gps data and store it in a file
    os.system("./setupGPS.sh %s" % directory)

    print("==============================================================\n")
    print("Total time: %s" % ((after) - (before)))
    print("==============================================================\n")

####################
if __name__ == '__main__':
    main()