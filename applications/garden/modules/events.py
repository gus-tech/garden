#!/usr/bin/env python

from __future__ import print_function
from datetime import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import urllib2
from globals import *
from outlets import *


color_ids = {}
color_ids['bold blue']  = 9   # color: #5484ed, index: 0
color_ids['blue']       = 1   # color: #a4bdfc, index: 1
color_ids['turquoise']  = 7   # color: #46d6db, index: 2
color_ids['green']      = 2   # color: #7ae7bf, index: 3
color_ids['bold green'] = 10  # color: #51b749, index: 4
color_ids['yellow']     = 5   # color: #fbd75b, index: 5
color_ids['orange']     = 6   # color: #ffb878, index: 6
color_ids['red']        = 4   # color: #ff887c, index: 7
color_ids['bold red']   = 11  # color: #dc2127, index: 8
color_ids['purple']     = 3   # color: #dbadff, index: 9
color_ids['gray']       = 8   # color: #e1e1e1, index: 10


def get_calendar(credentials_file = "credentials.json", SCOPES = ['https://www.googleapis.com/auth/calendar.events']):
    # If modifying default SCOPES, delete the file token.pickle
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token: creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token: pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)


def sync_events(db, max_results = 12, events_log_file = "events.log"):
    delete_past_events(db, commit=False)
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    for room in db().select(db.rooms.ALL):
        try:
            print('Getting the upcoming {} events for room {}: {}'.format(max_results, room['id'], room['name']))
            events_result = get_calendar().events().list(
                    calendarId=room['calendar_id'], timeMin=now, maxResults=max_results, singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])
            for event in events:
                start_time = datetime.strptime(event['start'].get('dateTime', event['start'].get('date'))[:-6], '%Y-%m-%dT%H:%M:%S')
                end_time = datetime.strptime(event['end'].get('dateTime', event['end'].get('date'))[:-6], '%Y-%m-%dT%H:%M:%S')
                db.events.update_or_insert(db.events.event_id == event['id'], event_id=event['id'],
                                           calendar_id=room['calendar_id'], room_id=room['id'],
                                           start_time=start_time, end_time=end_time, dict=event,)
        except:
            message = "Failed to get events for room {}: {} - calendar_id: {}".format(room['id'], room['name'], room['calendar_id'])
            print(message)
            with open(events_log_file, "a") as events_log:
                events_log.write("{} {}\n".format(str(datetime.now()).split('.')[0], message))
    db.commit()


def handle_events(db):
    events = get_current_events(db)
    for event in events:
        print(event['dict']['summary'])
        handle_outlets(db, event)


def handle_outlets(db, event):
    outlets = get_outlets(db, event['room_id'])
    for outlet in outlets:
        device_action = event['dict']['summary'].split(' ', 1)
        device = device_action[0].strip().lower()
        try:
            action = device_action[1].strip().lower()
            if outlet['name'].lower() == device:
                print(event['id'], event['dict']['summary'])
                set_outlet(db, outlet, action)
                db(db.events.id == event['id']).update(completed=True)
                db.commit()
                event['dict']['colorId'] = color_ids['bold green']
                update_event(event)
        except:
            try:
                event['dict']['colorId'] = color_ids['bold red']
                update_event(event)
                continue
            except: continue


def load_dicts(events):
    for event in events: event['dict'] = json.loads(event['dict'])
    return events


def get_events(db):
    return load_dicts(db().select(db.events.ALL)).as_list()


def get_current_events(db, room_id=None):
    sql = "SELECT * FROM events WHERE start_time <= datetime('now','localtime') AND end_time >= datetime('now','localtime') AND completed IS NULL"
    if room_id: sql + " AND room_id == {}".format(room_id)
    events = db.executesql(sql, as_dict=True)
    return load_dicts(events)


def delete_event(event, commit=True):
    db(db.events.id == event['id']).delete()
    if commit: db.commit()


def delete_events(events, commit=True):
    for event in events: delete_event(event, commit=False)
    if commit: db.commit()


def delete_past_events(db, commit=True):
    db.executesql("DELETE FROM events WHERE end_time < datetime('now','localtime')")
    if commit: db.commit()


def update_event(event):
    get_calendar().events().update(calendarId=event['calendar_id'], eventId=event['event_id'], body=event['dict']).execute()


def update_events(events):
    for event in events: update_event(event)


if __name__ == '__main__':
    from db import *
    if len(sys.argv) <= 1: sync_events(db)
    else:
        for arg in sys.argv:
            try: locals()[arg](db)
            except: pass
