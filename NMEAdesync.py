#!/usr/bin/env python3
# coding=utf-8


"""
NMEAdesync.py is a tool which through NMEA serial data will move time backwards on a NTPd server

command:
    NMEAdesync.py
    
To configure the running please edit NMEAdesync.cfg and the logging configuration in logging.cfg
"""


import sys
import configparser
import logging
import logging.config
from datetime import datetime, timedelta
from time import sleep
import threading
#import RPi.GPIO as GPIO


__author__ = 'Karit'
__copyright__ = 'Copyright 2017 Karit'
__license__ = 'MIT'
__version__ = '0.1'

def run_NMEAdesync():

    if cfg.getboolean('pps', 'pps_enabled'):
        import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
        outputPin = cfg.getint('pps', 'pin')
        GPIO.setup(outputPin, GPIO.OUT)

        iterationTime = cfg.getfloat('time', 'iteration_time')
        tenthTterationTime = iterationTime/10

    if cfg.getboolean('time', 'start_with_current_time'):
        runningTime = datetime.now()
    else:
        runningTime = datetime.strptime(cfg.get('time', 'start_time'), '%Y-%m-%d %H:%M:%S')

    stepTime = cfg.getfloat('time', 'step_time')
    iterationTime = cfg.getfloat('time', 'iteration_time')
    
    while True:
        print(generate_gprmc_line(runningTime))
        print(generate_gpgga_line(runningTime))
        runningTime = runningTime + timedelta(seconds=stepTime)
        if cfg.getboolean('pps', 'pps_enabled'):
            GPIO.output(outputPin, GPIO.HIGH)
            sleep(tenthTterationTime)
            GPIO.output(outputPin, GPIO.LOW)
            sleep(tenthTterationTime*9)
        else:
            sleep(iterationTime)
 
def generate_gpgga_line(lineTime):
    logger.debug('Running generate_gpgga_line with time: %s'%(lineTime))

    messageType = 'GPGGA'
    time = lineTime.strftime('%H%M%S.000')
    latitude = cfg.get('location', 'latitude')
    northOrSouth = cfg.get('location', 'latitude_north_or_south')
    longitude = cfg.get('location', 'longitude')
    westOrEast = cfg.get('location', 'longitude_west_or_east')
    fixQuality = 1
    numberOfSatellites = 10
    hdop = 0.96
    altitude = cfg.getfloat('location', 'altitude')
    altitudeUnits = 'M'
    heightAboveWGS84 = cfg.getfloat('location', 'altitude')
    heightAboveWGS84Units = 'M'
    dgpsAge = ''
    dgpsStationID = ''
    
    stringToChecksum = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (messageType,time, latitude, northOrSouth, longitude, westOrEast, fixQuality, numberOfSatellites, hdop, altitude, altitudeUnits,  heightAboveWGS84, heightAboveWGS84Units, dgpsAge, dgpsStationID)
    checksum = nmea_checksum(stringToChecksum)

    nmeaOuput = '$%s*%s' % (stringToChecksum, checksum)

    logger.debug('Return from generate_gprmc_line with: %s'%(nmeaOuput))
    return nmeaOuput

def generate_gprmc_line(lineTime):
    logger.debug('Running generate_gprmc_line with time: %s'%(lineTime))

    messageType = 'GPRMC'
    time = lineTime.strftime('%H%M%S.000')
    receiverWarning = 'A'
    latitude = cfg.get('location', 'latitude')
    northOrSouth = cfg.get('location', 'latitude_north_or_south')
    longitude = cfg.get('location', 'longitude')
    westOrEast = cfg.get('location', 'longitude_west_or_east')
    knots = cfg.get('location', 'knots')
    trueHeading = cfg.get('location', 'true_heading')
    date = lineTime.strftime('%d%m%y')
    magneticVariation = ''
    magneticVariationDirection = ''
    
    stringToChecksum = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,A' % (messageType,time, receiverWarning, latitude, northOrSouth, longitude, westOrEast, knots, trueHeading, date, magneticVariation, magneticVariationDirection)
    checksum = nmea_checksum(stringToChecksum)

    nmeaOuput = '$%s*%s' % (stringToChecksum, checksum)

    logger.debug('Return from generate_gprmc_line with: %s'%(nmeaOuput))
    return nmeaOuput

def nmea_checksum(stringToChecksum):
    """https://doschman.blogspot.co.nz/2013/01/calculating-nmea-sentence-checksums.html"""
    checksum = 0
    
    for c in stringToChecksum:
       checksum ^= ord(c)
    
    checksum = hex(checksum)
    checksum = checksum[2:]
    return (checksum)

def shut_down():
    """
    Closes connections and threads
    """
    logger.info('Keyboard interrupt received. Terminated by user. Good Bye.')
    sys.exit(1)

def start_script():
    global cfg
    cfg = configparser.ConfigParser()
    cfg.read('NMEAdesync.cfg')
    
    global logger
    logging.config.fileConfig('logging.cfg')
    logger = logging.getLogger(__name__)
    logger.info('Starting NMEAdesync')

   

    
    try:
        run_NMEAdesync()
    except KeyboardInterrupt:
        shut_down()
    except (OSError, IOError) as error:
        sys.stderr.write('\rError--> {}'.format(error))
        logger.error('Error--> {}'.format(error))
        sys.exit(1)

if __name__ == '__main__':
    start_script()
