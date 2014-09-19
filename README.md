mbile-backend
==============

Backend for HTN iOS and Android app.

Usage
-----

There are two ways of interacting with the datastore: issuing an update, and
modifying the static datastore.

### Issuing Updates

This is the mechanism for issuing live updates to all users of the application.
There is a script set up to do all the required steps; all that you have to do
is configure the system and run the script.

Fortunately, we have an amazon EC2 instance set up with all the configuration
details (though it is documented below anyways). Contact @srcreigh for
information on how to access this machine.

Once you connect to the instance via `ssh`, you can just go to this repository
on the machine and run the script:

```bash
cd mobile-backend
python issue-update.py
```

This will guide you through entering the name (i.e. title), text (i.e. body
text), and an optional image url which will be circle-cropped and displayed as
an avatar.

### Updating Firebase

The data from the app is loaded from Firebase, at
`https://hackthenorth.firebaseio.com/mobile`. There is a data point for each of
the tabs in each app:

`/updates`, `/schedule`, `/prizes`, `/mentors`, `/team`, and `/sponsors`.

Note: do not interact with the /updates information manually; use the
`issue-update.py` script as explained above.

If you have access to the Firebase Forge for `hackthenorth`, then you can
use that to add data or modify points. There is data in the datastore currently
that can serve as examples for required fields, datetime formatting
conventions, etc. This is the easiest option for easy editing and adding of
data. Otherwise, you will have to use some other API to interact with firebase.

#### Be careful...

* Know the difference between post, put, and patch requests when working with
  firebase.

#### Interacting with Firebase

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

Otherwise, you should write a python script. The requests will be analogous to
the repl.

Install
-------

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
