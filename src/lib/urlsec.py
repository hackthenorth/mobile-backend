#!/bin/python

# Keeps track of the least recently used URLs
# Author: Shane Creighton-Young

import os
import json
import datetime
import itertools
from ..login import *

DATA_FILENAME = 'urlsec.json'

def get_data():
   path = os.path.expanduser(CONFIG_PATH)

   if not os.path.exists(path):
      os.makedirs(path)

   try:
      f = open(os.path.join(path, DATA_FILENAME), 'r')
   except IOError as e:
      return {} 
   else:
      with f:
         return json.load(f)

def put_data(data):
   path = os.path.expanduser(CONFIG_PATH)

   if not os.path.exists(path):
      os.makedirs(path)

   with open(os.path.join(path, DATA_FILENAME), 'w') as f:
      json.dump(data, f)

# name: String, url: String
# Tell us that this URL was used!
def use(name, url):
   data = get_data()

   if url != '':
      key = 'N' + name + 'U' + url

      # Add this entry to the dict
      epoch_time = datetime.datetime.now().strftime('%s')
      entry = { 'name': name, 'url': url, 'time': epoch_time }
      data[key] = entry

      put_data(data)

# n: Integer
# Get the n most recently used URLs with names
def get_recent(n):
   data = get_data().values()

   # Sort by the key of the tuples, which is the epoch time 
   # that it was last used
   data = sorted(data, key=lambda x: x['time'], reverse=True)

   # Take the first n elements
   data = data[0:n]

   # Remove the keys (they're unnecessary) and return
   return data

