#!/bin/python

import json
import requests

from src.login import *

with open('test-data/prizes.json', 'r') as f:
    prizes = json.load(f)

    for prize in prizes:

        params = {
                'auth': FIREBASE_SECRET
                }

        r = requests.post('%s/prizes.json' % FIREBASE_URL,
                data = json.dumps(prize), params = params)
        print r.json()
