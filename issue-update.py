#!/bin/python

from src.lib import updates

if updates.checkEnvVars():
    data = updates.getDataFromUser()
    if data is not None:
        updates.pushToFirebase(data)
        updates.pingGCM(data)
        updates.pingAPNS(data)


