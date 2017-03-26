# NMEAdesync
NMEAdesync is a tool which will output NMEA sentences to stdout. Using [socat](http://www.dest-unreach.org/socat/) you can redirect this output to NTPd and move time. NMEAdesync will be first prensented during a conference talk at [BSidesCBR 2017](http://www.bsidesau.com.au/speakers.html#david).

NMEAdesync will send NMEA senetences with a spoof time to NTPd and also a spoofed PPS 

## Requirements
NTPd using NMEA data over serial as the time, with PPS for accuarete timing. I set up a Pi using this [guide](https://frillip.com/raspberry-pi-stratum-1-ntp-server/).

## Running
1. Configure the options in NMEAdesync.cfg
1. Connect to the PPS wire to GPIO pint 25
1. sudo rm /dev/gps0 
1. socat -d -d pty,raw,echo=0 "exec:/home/pi/NMEAdesync.py,pty,raw,echo=0"
1. Note the pts number as will need to use it in the next step
1. sudo ln -s /dev/pts/1 /dev/gps0
1. Notice the time has changed
1. Check pps sudo ppstest /dev/pps0
