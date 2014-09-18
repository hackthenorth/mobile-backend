mobile-backend
==============

Backend for HTN iOS and Android app.

Setup
-----

```bash
sudo pip install -r requirements.txt
```

Then, create a file `src/login.py`, with the following contents:

```python
#!/bin/python

FIREBASE_SECRET="[firebase secret here]"
GCM_API_KEY="[gcm api key here]"

# Not really secret, but these are configuration options too:
FIREBASE_URL="https://your-firebase.firebaseio.com"
CONFIG_PATH="~/.htn-mobile-backend"
```

Note that you must have your IP address on the whitelist in the Google Developers
Console to send updates via GCM.

### Be careful...

* know the difference between post, put, and patch requests when working with
  firebase.

### Interacting with Firebase

For quick and dirty operations, it's easy enough to start a python repl in the
root of this repository:

```bash
$ cd mobile-backend/
$ python

>>> # note: this is untested
>>> from src.login import *
>>> import requests
>>> import json
>>> FIREBASE_URL
'https://hackthenorth.firebaseio.com/mobile'
>>> FIREBASE_SECRET
[ secret ]
>>> r = requests.patch('%s/team.json', data=json.dumps({'abc123':{'name':'Shane'}}), params={'auth':FIREBASE_SECRET'})
```

Otherwise, you should write a python script, where the requests are about the
same.
