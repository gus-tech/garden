#!/usr/bin/env python

from globals import *
import json

gpio_root = "/sys/class/gpio/gpio"


def action2int(action):
    string = str(action).lower().strip()
    if string == "on" or action == 1: return 1
    else: return 0


def get_light(db, light_id):
    light = db(db.lights.id == light_id).select(db.lights.ALL).first()
    light['name'] = light['name'].strip()
    return light


def get_lights(db, room_id=None):
    if room_id: lights = db(db.lights.room_id == room_id).select(db.lights.ALL)
    else: lights = db().select(db.lights.ALL)
    for light in lights:
        light['name'] = light['name'].strip()
    return lights


def set_light(db, light, action, commit=True): # on/off
    action = action2int(action)
    with open(gpio_root + str(light['gpio']) + "/value", 'w') as value: value.write(str(action))
    light['state_'] = action
    light.update_record()
    if commit: db.commit()
    return light




if __name__ == '__main__':
    from db import *
    set_light(db, get_light(db, 1), 1)

    """
    if len(sys.argv) <= 1: get_states(db, get_outlets(db))
    else:
        for arg in sys.argv:
            try: locals()[arg](db)
            except: pass
    """
