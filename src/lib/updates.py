#!/bin/python

import httplib
import time
import json
import os
import sys
import requests
import re

# IO helper functions
from htnio import *

# The narrative in the comments for this code is as follows:
# 'the user' is a user of our app, who we are sending notifications to
# 'the/an admin' is a user of this script

# Environment variables, URLs, and other constants
from ..login import * # Contains all the secret login info
GCM_URL = 'https://android.googleapis.com/gcm/send'

def getCurrentTimeISO8601():
   # Note: this assumes EST with daylight saving's time.
   return time.strftime('%Y-%m-%dT%H:%M:%S-04:00')

# Checks that environment variables exist and that they work correctly.
# Returns True if so, and False otherwise.
def checkEnvVars():

   # Check that the firebase secret is valid. Note that foo.firebaseio.com/test.json 
   # is a valid data path that doesn't have public read permission, so we should only 
   # be able to read it if the secret is valid.
   printInfo('Checking that the Firebase secret is valid...')
   r = requests.get("%s/test.json" % FIREBASE_URL, params = { 'auth': FIREBASE_SECRET })
   if 'error' in r.json():
       printError("Firebase error: '%s'" % r.json()['error'])
       printError('Double check that $FIREBASE_SECRET matches the secret ' \
             'for %s' % FIREBASE_URL)
       print ''
       return False
   printInfo('Firebase secret OK')

   # This sends a dummy GCM request that won't actually do anything meaningful. However,
   # it will give an error if the API key is invalid for some reason.
   printInfo('Checking that the GCM API key is valid...')
   kwargs = { 
         'headers': { 
            'Authorization': 'key=%s' % GCM_API_KEY, 
            'Content-Type': 'application/json' 
            }, 
         'data': json.dumps({ 'registration_ids': [ '40' ] })
         }
   r = requests.post(GCM_URL, **kwargs)

   try:
      # GCM returns non-json data on error.
      r.json()
   except ValueError:
      printError('GCM authorization error: %s' % r.text)
      printError('Check that your GCM_API_KEY is correct, and that your IP address ' \
            'is registered in the GCM dashboard.')
      return False
   printInfo('GCM API key OK')

   # If we get here, then our environment variables are all good. :+1:
   return True

# Returns a dict of the new data on success, or None if failed.
def pushToFirebase():

   # Read the data for the update.
   print ''
   name = forever_raw_input(make_prompt('name'))
   description = forever_raw_input(make_prompt('text'))
   printInfo('Note that you can hit just hit <enter> to use the default image.')
   imageurl = raw_input(make_prompt('image url'))

   # Confirm
   new_data = { 'name': name,
                'description': description,
                'avatar': imageurl,
                'time': getCurrentTimeISO8601() }
   print ''
   printInfo('Confirm update:')
   print json.dumps(new_data, indent=2)

   # Keep taking input until the admin write something that resembles yes or no
   while True:
       confirm = raw_input(make_prompt('yn')).lower()
       if confirm[0] == 'y' or confirm[0] == 'n':
           break

   if confirm[0] == 'n':
       printInfo('Cancelled')
       return None

   # Note: confirm[0] must be 'y...' at this point, so we can assume the admin
   # has said "yes this data is good"

   # Add the update to firebase.
   r = requests.post('%s/updates.json' % FIREBASE_URL,
                     data = json.dumps(new_data),
                     params = { 'auth': FIREBASE_SECRET })

   # Check for errors
   if 'error' in r.json():
       printError('Firebase error: %s' % r.json()['error'])
       return None

   printInfo('Data successfully added to Firebase')
   return new_data

# Takes a dict of data that corresponds to the data that was just added to 
# Firebase, and sends a notification to all our users about the new update.
#
# TODO: The GCM payload is max 4kb, and we currently aren't doing any checking
# on the size of the payload, and if GCM fails then, by the way this code is 
# structured, we won't be able to send users notifications for this update.
#
# TODO: Can probably add functionality here to send a notification for the 
# most recent update in /updates.json, and have another admin script that uses
# it in the case that GCM fails for some reason and we didn't send the users
# notifications.
#
# TODO: We can only send 1000 registration_ids at a time to GCM. To be safe we should
# probably check for this and use a loop for multiple requests.
def pingGCM(data):

   # Get all the android registration ids from Firebase
   print ''
   printInfo('Sending notifications to Android users...')
   printInfo('Getting registration ids from /notifications/android.json...')
   r = requests.get('%s/notifications/android.json' % FIREBASE_URL,
                    params = { 'auth': FIREBASE_SECRET })

   registration_ids = []

   # If we didn't have any registration IDs in Firebase, we will get back None as our
   # JSON; don't try to use it if it's None.
   if r.json():
      if 'error' in r.json():
         printError('Error retreiving registration ids from /notifications/android.json')
         printError('Make sure the Firebase instance at %s is properly set up with ' \
               'registration ids at /notifications/android.' % FIREBASE_URL)
         printError('Also, make sure to call checkEnvVars to validate your environment ' \
               'variables.')
      else:
         registration_ids = r.json().keys()

   # If there aren't any registration IDs, then stop doing things.
   if len(registration_ids) == 0:
      printInfo('No registration IDs in Firebase')
      printInfo('Finishing')
      return None

   # Make the request to GCM.
   kwargs = {
         'headers': {
            'Content-Type': 'application/json',
            'Authorization': 'key=%s' % GCM_API_KEY
            },
         'data': json.dumps({
            'registration_ids': registration_ids,
            'data': data
            })
         }
   r = requests.post(GCM_URL, **kwargs)

   # Check for GCM errors here
   try:
      r.json()
   except ValueError:
      printError('GCM error: %s' % r.text)
      return None

   # See [1] for a reference on the result values of these kinds of GCM requests.
   # Thankfully they're pretty sane.
   # [1]: https://developer.android.com/google/gcm/http.html#example-responses

   # r.json()['success'] and failure report the number of successful and failed
   # notifications, respectively.
   printInfo('%d notifications sent successfully.' % r.json()['success'])
   printInfo('%d notifications failed.' % r.json()['failure'])

   # When we send off a GCM request, sometimes GCM will have something to say about
   # the registration IDs we tried to send a message to.
   print ''
   printInfo('Performing bookkeeping...')
   results = r.json()['results']
   for i in xrange(0, len(registration_ids)):

      registration_id = registration_ids[i]
      result = results[i]

      if 'error' in result:
         # GCM will give us this result if we give it a) a malformed registration ID,
         # or b) an ID that corresponds to a user who has uninstalled our app. In both cases,
         # we should delete the registration ID from firebase.
         if result['error'] == 'Unregistered' or result['error'] == 'InvalidRegistration':

            # Delete the registration ID from firebase.
            printInfo('Registration ID \'%s\' is invalid; deleting from Firebase...' % registration_id)
            r = requests.delete('%s/notifications/android/%s.json' % (FIREBASE_URL, registration_id),
                  params = { 'auth': FIREBASE_SECRET })
            
      # Sometimes GCM will be like 'yo! you gave me this registration ID, but I have a new one for this
      # user and in the future you should use it instead'.
      elif 'registration_id' in result:

         new_regid = result['registration_id']

         # Update the registration ID from firebase
         printInfo('Updating registration ID %s to %s...' % (registration_id, new_regid))
         r = requests.delete('%s/notifications/android/%s.json' % registration_id,
               params = { 'auth': FIREBASE_SECRET })
         r = requests.put('%s/notifications/android/%s.json' % new_regid,
               params = { 'auth': FIREBASE_SECRET })
