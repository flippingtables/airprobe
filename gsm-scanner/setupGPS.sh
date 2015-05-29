#! /bin/sh

#script takes at least 1 argument,  which is the directory that we want to store the gps data in
echo $1

#forward the port for gps data from the phone
/home/openbts/Downloads/android-sdk-linux/platform-tools/adb forward tcp:4352 tcp:4352

#start the gpsd daemon
gpsd -n -D5 tcp://localhost:4352

#get some gps data and dump it in a file.
DIRECTORY="$1gps.json"
gpspipe -w -n 20 | grep "lon" > $DIRECTORY