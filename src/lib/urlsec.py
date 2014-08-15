#!/bin/python

# Keeps track of the least recently used URLs
# Author: Shane Creighton-Young

import os
import json
import datetime
import itertools
from ..login import *

def get_data():
   path = os.path.expanduser(os.path.join(CONFIG_PATH, 'urlsec.json'))

   if not os.path.exists(os.path.expanduser(CONFIG_PATH)):
       os.makedirs(os.path.expanduser(CONFIG_PATH))

   try:
      f = open(path, 'r')
   except IOError:
      return {}
   else:
      with f:
         return json.load(f)

def put_data(data):

   if not os.path.exists(os.path.expanduser(CONFIG_PATH)):
       os.makedirs(os.path.expanduser(CONFIG_PATH))

   path = os.path.expanduser(os.path.join(CONFIG_PATH, 'urlsec.json'))
   with open(path, 'w') as f:
      json.dump(data, f)

# name: String, url: String
# Tell us that this URL was used!
def use(name, url):
   data = get_data()

   # Remove potential duplicate
   data = { k:data[k] for k in data if data[k]['url'] != url or data[k]['name'] != name }

   # Add this entry to the dict
   epoch_time = datetime.datetime.now().strftime('%s')
   data[epoch_time] = { 'name': name, 'url': url }
   put_data(data)

# n: Integer
# Get the n most recently used URLs with names
def get_recent(n):
   data = get_data().items()

   # Sort by the key of the tuples, which is the epoch time 
   # that it was last used
   data = sorted(data, key=lambda tup: tup[0], reverse=True)

   # Take the first n elements
   data = data[0:n]

   # Remove the keys (they're unnecessary) and return
   return map(lambda tup: tup[1], data)

