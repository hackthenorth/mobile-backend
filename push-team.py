#!/bin/python

import json
import requests

from src.login import *

with open('data/team_data.json', 'r') as f:
    teammembers = json.load(f)

    for teammember in teammembers:

        params = {
                'auth': FIREBASE_SECRET
                }

        r = requests.post('%s/team.json' % FIREBASE_URL,
                data = json.dumps(teammember), params = params)
        print r.json()

