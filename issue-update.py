#!/bin/python

import httplib
import time
import json
import os
import sys
import requests
import re
from termcolor import colored

FIREBASE_URL = 'https://shane-hackthenorth.firebaseio.com/'
FIREBASE_SECRET = os.getenv('FIREBASE_SECRET', None)

def printError(msg):
    print "[ %s ] %s" % (colored('ERROR', 'red'), msg)

def printInfo(msg):
    print "[ %s ] %s" % (colored('INFO', 'green'), msg)

def exit(n):
    print ""
    sys.exit(n)

INPUT_INDICATOR = '> '
def make_prompt(string):
    return "\n[ %s ]\n%s" % (string, INPUT_INDICATOR)

def forever_raw_input(string):
    input_string = raw_input(string)
    while True:
        if input_string != '':
            return input_string
        input_string = raw_input(INPUT_INDICATOR)

def getCurrentTimeISO8601():
    # Note: this assumes EST with daylight saving's time.
    return time.strftime("%Y-%m-%dT%H:%M:%S-04:00")

def push(path, data):
    requests

print ""

# Check environment variables.
if FIREBASE_SECRET is None:
    printError("You have not set your FIREBASE_SECRET environment variable.")
    exit(1)

# Check that the firebase secret is valid. Note that foo.firebaseio.com/test.json 
# is a valid that doesn't have public read permission, so we should only be able
# to read it if the secret is valid.
printInfo('Checking that the Firebase secret is valid...')
r = requests.get("%s/test.json" % FIREBASE_URL, params = { 'auth': FIREBASE_SECRET })
if 'error' in r.json():
    printError("Firebase error: '%s'" % r.json()['error'])
    printError("Double check that $FIREBASE_SECRET matches the secret for %s" % FIREBASE_URL)
    exit(1)
printInfo('Firebase secret OK')

# Read the data for the update.
name = forever_raw_input(make_prompt('Author Name'))
description = forever_raw_input(make_prompt('Update Text'))
imageurl = raw_input(make_prompt('Avatar Image Url (or enter for default image)'))

# Confirm
new_data = { 'name': name,
             'description': description,
             'avatar': imageurl,
             'time': getCurrentTimeISO8601() }
print ""
printInfo("Confirm update:")
print json.dumps(new_data, indent=2)
while True:
    confirm = raw_input(make_prompt('yn')).lower()
    if confirm[0] == 'y' or confirm[0] == 'n':
        break

if confirm[0] == 'y':
    # Add the update to firebase.
    r = requests.post('%s/updates.json' % FIREBASE_URL,
                      data = json.dumps(new_data),
                      params = { 'auth': FIREBASE_SECRET })

    if 'error' in r.json():
        printError('Firebase error: %s' % r.json()['error'])
    else:
        print ""
        printInfo('Success')
        exit(0)

elif confirm[0] == 'n':
    print ""
    printInfo('Cancelled')
    exit(1)


