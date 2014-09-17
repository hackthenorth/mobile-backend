#!/bin/python

import json
import requests

from src.login import *

with open('data/cleaned-responses.json', 'r') as f:
    mentors = json.load(f)

    for mentor in mentors:

        params = {
                'auth': FIREBASE_SECRET
                }

        r = requests.post('%s/mentors.json' % FIREBASE_URL,
                data = json.dumps(mentor), params = params)
        print r.json()
