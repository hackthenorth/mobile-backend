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
