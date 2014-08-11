#!/bin/python

import httplib
import time
import json
import os
import sys
import requests
import re
import copy

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
   r = requests.get('%s/test.json' % FIREBASE_URL, params = { 'auth': FIREBASE_SECRET })
   if 'error' in r.json():
       printError("Firebase error: '%s'" % r.json()['error'])
       printError('Double check that $FIREBASE_SECRET matches the secret ' \
             'for %s.' % FIREBASE_URL)
       print ''
       return False
   printInfo('Firebase secret OK.')

   # This sends a dummy GCM request that won't actually do anything meaningful. However,
   # it will give an error if the API key is invalid for some reason.
   printInfo('Checking that the GCM API key is valid...')
   args = { 
         'headers': { 
            'Authorization': 'key=%s' % GCM_API_KEY, 
            'Content-Type': 'application/json' 
            }, 
         'data': json.dumps({ 'registration_ids': [ '40' ] })
         }
   r = requests.post(GCM_URL, **args)

   try:
      # GCM returns non-json data on error.
      r.json()
   except ValueError:
      printError('GCM authorization error: %s' % r.text)
      printError('Check that your GCM_API_KEY is correct, and that your IP address ' \
            'is registered in the GCM dashboard.')
      return False
   printInfo('GCM API key OK.')

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

   # Keep taking input until the admin writes something that resembles yes or no
   while True:
       confirm = raw_input(make_prompt('y/n')).lower()
       if len(confirm) > 0 and confirm[0] in ['y', 'n']:
           break

   if confirm[0] == 'n':
       printInfo('Cancelled.')
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

   printInfo('Data successfully added to Firebase.')
   return new_data


# GCM payload can't be more than 4096 bytes.
def normalizeGCMData(data):
   newData = copy.deepcopy(data)

   # calculate the size of the payload
   size = 0;
   for key in newData.keys():
      size += len(bytes(key)) + len(bytes(newData[key]))

   if size > 4096:
      delta = size - 4096

      # Trim at least as many bytes off as we need to be trimmed
      string = newData['description'][:-delta] 

      # Put a '...' on the end of the string
      string = '%s%s' % (string[:-3], '...')
      newData['description'] = string

   return newData


def partition(lst, n):
   # j partititions of i elements
   lsts = [[lst[i + n*j] for i in range(0, n)] for j in range(0, len(lst)/n)]
   if len(lst) % n == 0:
      return lsts
   else:
      # Append on the overflow elements
      return lsts + [ lst[n * (len(lst)/n):] ]


# TODO: Can probably add functionality here to send a notification for the 
# most recent update in /updates.json, and have another admin script that uses
# it in the case that GCM fails for some reason and we didn't send the users
# notifications.

# Takes a dict of data that corresponds to the data that was just added to 
# Firebase, and sends a notification to all our users about the new update.
def pingGCM(data):

   # Normalize the data
   data = normalizeGCMData(data)

   # Get all the android registration ids from Firebase
   print ''
   printInfo('Sending notifications to Android users...')
   printInfo('Getting registration ids from /notifications/android.json...')
   r = requests.get('%s/notifications/android.json' % FIREBASE_URL,
                    params = { 'auth': FIREBASE_SECRET })

   registration_ids = []

   # If we didn't have any registration IDs in Firebase, we will get back None as our
   # JSON; don't try to use it if it's None.
   response = r.json() # is a python dict
   if response:
      if 'error' in response:
         printError('Error retreiving registration ids from /notifications/android.json')
         printError('Make sure the Firebase instance at %s is properly set up with ' \
               'registration ids at /notifications/android.' % FIREBASE_URL)
         printError('Also, make sure to call checkEnvVars to validate your environment ' \
               'variables.')
      else:
         registration_ids = response.keys()

   # If there aren't any registration IDs, then stop doing things.
   if len(registration_ids) == 0:
      printInfo('No registration IDs in Firebase.')
      printInfo('Finished.')
      return None
   else:
      printInfo('Received registration ids.')
      print ''

   # GCM only supports requests with up to 1000 registration IDs, so 
   # partition the registration_ids into lists of <= 1000 ids.
   regid_partition = partition(registration_ids, 1000)

   for i in xrange(0, len(regid_partition)):
      registration_ids = regid_partition[i]

      printInfo('Making GCM request %d of %d...' % (i, len(regid_partition)))
      
      # Make the request to GCM.
      args = { 
              'headers': { 
                  'Content-Type': 'application/json',
                  'Authorization': 'key=%s' % GCM_API_KEY
                  },
              'data': json.dumps({
                  'registration_ids': registration_ids,
                  'data': data 
                  })
              }
      r = requests.post(GCM_URL, **args)

      # Check for GCM errors here
      gcm_response = None
      try:
         gcm_response = r.json()
      except ValueError:
         printError('GCM error: %s' % r.text)
         return None

      # See [1] for a reference on the result values of these kinds of GCM requests.
      # Thankfully they're pretty sane.
      # [1]: https://developer.android.com/google/gcm/http.html#example-responses

      # gcm_response['success'] and 'failure' report the number of successful and failed
      # notifications, respectively.
      printInfo('%d notifications sent successfully.' % gcm_response['success'])
      printInfo('%d notifications failed.' % gcm_response['failure'])

      # When we send off a GCM request, sometimes GCM will have something to say about
      # the registration IDs we tried to send a message to.
      print ''
      printInfo('Performing bookkeeping...')
      results = gcm_response['results']
      for i in xrange(0, len(registration_ids)):

         registration_id = registration_ids[i]
         result = results[i]

         if 'error' in result:
            # GCM will give us this result if we give it a) a malformed registration ID,
            # or b) an ID that corresponds to a user who has uninstalled our app. In both cases,
            # we should delete the registration ID from firebase.
            if result['error'] in ['Unregistered', 'InvalidRegistration']:

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

      printInfo('Bookkeeping finished')
