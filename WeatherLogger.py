#!/usr/bin/env python

# This program uses the BME_280 sensor using I2c
# and Adafruit GPIO module library
# This program uses two LEDs, one connected to GPIO pin 32, the other connected to
# pin 37.
# The program turns different LEDs on and off depending on the temperature.

# Author: Aydin Zaman
# 2017-04-01

# 1. Change the example.py to post data to a rest api
# 2. Added basic logging of information to a file instead of the console
# Ashar Zaman
# 2017-10-08

import sys
import traceback
import time
import RPi.GPIO as GPIO
import requests
import logging

from Adafruit_BME280 import *

degrees = 0
fah = 0
hectopascals = 0
humidity = 0
GPIO.setmode(GPIO.BOARD)

# Looking up the sensor and setting it for output
redpin = 32
greenpin = 37

sensor = BME280(mode=BME280_OSAMPLE_8)
GPIO.setup(redpin, GPIO.OUT)
GPIO.setup(greenpin, GPIO.OUT)


def blinkLED():
    # Turning the LEDs on and off
    if fah < 80.0 and fah > 70.0:
        GPIO.output(greenpin, GPIO.HIGH)
        GPIO.output(redpin, GPIO.LOW)
    else:
        GPIO.output(greenpin, GPIO.LOW)
        GPIO.output(redpin, GPIO.HIGH)


def readSensor():
    global degrees, fah, pascals, hectopascals, humidity

    # Changing the mode to BOARD (pin number on the board)
    degrees = sensor.read_temperature()
    fah = 9.0 / 5.0 * degrees + 32
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()


def printInfo():
    logger.info('Fahrenheit= {0:0.3f} deg F'.format(fah))
    logger.info('Celsius   = {0:0.3f} deg C'.format(degrees))
    logger.info('Pressure  = {0:0.2f} hPa'.format(hectopascals))
    logger.info('Humidity  = {0:0.2f} %'.format(humidity))
    logger.info('==========={0}==========='.format(
        time.strftime("%Y-%m-%d %H:%M")))


def postData():
    url = "http://www.myapp.es/api/weather/"
    payload = {"Temp": fah, "Pressure": hectopascals, "Humidity": humidity,
               "DateCreated": time.strftime("%Y-%m-%d %H:%M:%S")}

    try:
        api = requests.post(url, data=payload)
        logger.info('data posted successfully')
    except Exception as e:
        logger.info(e, exc_info=True)
    finally:
        api.close()


def main_loop():
    while True:
        try:
            readSensor()
            printInfo()
            blinkLED()
            postData()
            time.sleep(60.0)
        except:
            logger.info("Oops...something went wrong")
            traceback.print_exc(file=sys.stdout)
            logger.info(traceback.print_exc)
            break


def setupLogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.FileHandler('run.log')
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    return logger

# The following makes this program start running at main_loop()
# when executed as a stand-alone program.
if __name__ == '__main__':
    try:

        logger = setupLogger()

        main_loop()
    except Exception as e:
        logger.info(e, exc_info=True)
        traceback.print_exc(file=sys.stdout)
    finally:
        # reset the sensor before exiting the program
        GPIO.cleanup()
