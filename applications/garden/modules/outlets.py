#!/usr/bin/env python

from globals import *
#from netaddr import *
import urllib2
import json


def get_outlet(db, outlet_id):
    outlet = db(db.outlets.id == outlet_id).select(db.outlets.ALL).first()
    outlet['name'] = outlet['name'].strip()
    outlet['mac'] = outlet['mac'].strip().lower() #EUI(outlet['mac'])
    outlet['ip'] = outlet['ip'].strip().lower()
    return outlet


def get_outlets(db, room_id=None):
    if room_id: outlets = db(db.outlets.room_id == room_id).select(db.outlets.ALL)
    else: outlets = db().select(db.outlets.ALL)
    for outlet in outlets:
        outlet['name'] = outlet['name'].strip()
        outlet['mac'] = outlet['mac'].strip().lower() #EUI(outlet['mac'])
        outlet['ip'] = outlet['ip'].strip().lower()
    return outlets


def set_outlet(db, outlet, action, timeout=3, commit=True): # on/off
    action = action.strip().lower()
    url = "http://{}/cgi-bin/json.cgi?set={}".format(outlet['ip'], action)
    try: outlet['state_'] = json.loads(urllib2.urlopen(url, timeout=timeout).read())['state']
    except: outlet['state_'] = json.loads(urllib2.urlopen(url, timeout=timeout).read())['state']
    outlet.update_record()
    if commit: db.commit()
    return outlet


def get_state(db, outlet, timeout=3, commit=True):
    url = "http://{}/cgi-bin/json.cgi?get=state".format(outlet['ip'])
    try: outlet['state_'] = json.loads(urllib2.urlopen(url, timeout=timeout).read())['state']
    except: outlet['state_'] = json.loads(urllib2.urlopen(url, timeout=timeout).read())['state']
    outlet.update_record()
    if commit: db.commit()
    return outlet


def get_states(db, outlets, timeout=3, commit=True):
    for outlet in outlets:
        try: get_state(db, outlet, timeout=timeout, commit=False)
        except: continue
    if commit: db.commit()
    return outlets


if __name__ == '__main__':
    from db import *
    if len(sys.argv) <= 1: get_states(db, get_outlets(db))
    else:
        for arg in sys.argv:
            try: locals()[arg](db)
            except: pass
