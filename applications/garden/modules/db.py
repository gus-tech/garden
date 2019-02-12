#!/usr/bin/env python

from globals import *


def define_tables(db):
    db.define_table('rooms',
                        Field('name', 'string'),
                        Field('calendar_id', 'string'),
                   )
    db.define_table('events',
                        Field('event_id', 'string'),
                        Field('calendar_id', 'string'),
                        Field('room_id', 'integer'),
                        Field('start_time', 'datetime'),
                        Field('end_time', 'datetime'),
                        Field('completed', 'boolean'),
                        Field('dict', 'json'),
                   )
    db.define_table('lights',
                        Field('name', 'string'),
                        Field('gpio', 'integer'),
                        Field('room_id', 'integer'),
                        Field('state_', 'string'),
                   )
    db.define_table('outlets',
                        Field('name', 'string'),
                        Field('mac', 'string'),
                        Field('ip', 'string'),
                        Field('room_id', 'integer'),
                        Field('state_', 'string'),
                   )
    return db


db = DAL("sqlite://" + project_path + "/" + app_path + "/" + db_path, migrate_enabled=False, fake_migrate=True)
define_tables(db)
