mobile-backend
==============

Backend for HTN iOS and Android app.

Setup
-----

```bash
sudo pip install -r requirements.txt
```

Then, create a file called secrets.txt, with the following contents:

```bash
export FIREBASE_SECRET="[firebase secret here]"
export GCM_API_KEY="[gcm api key here]"

# Not really secret, but this is a configuration option too:
export FIREBASE_URL="https://your-firebase.firebaseio.com"
```

Note that you must have your IP address on the whitelist in the Google Developers
Console to send updates via GCM. Last, run `. secrets.txt` before using any of 
the scripts. (You may set up your environment variables another way if you so desire).

