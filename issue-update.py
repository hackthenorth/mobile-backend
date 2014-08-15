#!/bin/python

from src.lib import updates

if updates.checkEnvVars():
    data = updates.pushToFirebase()
    if data is not None:
        updates.pingGCM(data)
        updates.pingAPNS(data)


