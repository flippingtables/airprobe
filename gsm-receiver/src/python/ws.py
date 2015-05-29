#!/usr/bin/env python

import os
import time
import sys
from optparse import OptionParser
import shutil
import socket
import subprocess
HOST = '127.0.0.1'	# Symbolic name, meaning all available interfaces
PORT = 4729	# GSMTAP sends UDP packages on this port

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def sendMessage(fileName, section):
	message = "%s for file: %s" % (section, fileName)
	s.sendto(message, (HOST, PORT))

def tshark(fileName):
    print("Starting tshark")
    script = "tshark -i lo -f 'udp port 4729' -Y 'gsmtap' -a duration:10 -T pdml > %s.xml" % fileName
    print(script)
    #os.system(script)
    subprocess.Popen(script, shell=True)
    #fileNameXML = '%s.xml' % fileName
    #os.spawnl(os.P_NOWAIT, '/usr/bin/tshark', '-i', 'lo', '-f', 'udp port 4729', '-Y', 'gsmtap', '-a', 'duration:10', '-T', 'pdml', '>', fileNameXML)
    #os.spawnl(os.P_NOWAIT, '/usr/bin/tshark', (script))

directory = "/home/openbts/Desktop/SCANTEST"
dest = "/home/openbts/Desktop/PCAPZ/"
def walkAllScannedFiles():
    print("Walking all directories")
    for root, _, files in os.walk(directory):
        for f in files:
            
            fullpath = os.path.join(root, f)
            quiet = "> /dev/null 2> /dev/null"
            #sendMessage(f, "/BEGINNING")   
            #sendMessage(f, "000000000000000000000000000000000")
            shellscript = "./gsm_receive.py -I %s -d 64 -c 0C %s" % (fullpath, quiet)
#            tshark(fullpath)
            
            script = "tshark -i lo -f 'udp port 4729' -Y 'gsmtap' -a duration:10 -T pdml > %s%s.xml" % (dest,f)
            print(script)
            p = subprocess.Popen(script, shell=True)
            time.sleep(1)
            print("Scanning: %s" % fullpath)
            os.system(shellscript)
            #subprocess.Popen(shellscript, shell=True)
            #time.sleep(15)
            #sendMessage(f, "/END")
            #sendMessage(f, "111111111111111111111111111111111")
            while p.poll() is None:
                time.sleep(0.5)
            print("NEXT FILE")
    print("Walking done")

walkAllScannedFiles()



