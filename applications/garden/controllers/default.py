# -*- coding: utf-8 -*-
#import datetime
from events import *
from outlets import *
from lights import *

# ---- example index page ----
def index():
    #response.flash = T("Hello World")
    rooms = db().select(db.rooms.ALL)
    outlets = {}
    events = {}
    lights = {}
    for room in rooms:
        events[room['id']] = get_current_events(db, room['id'])
        outlets[room['id']] = get_outlets(db, room['id'])
        lights[room['id']] = get_lights(db, room['id'])

    return dict(message=T('Welcome to web2py!'), rooms=rooms, events=events, outlets=outlets, lights=lights)


def sync():
    return response.json(dict(outlets=get_outlets(db), lights=get_lights(db)))


def set_device():
    try:
        action = request.vars['action']
        Type =   request.vars.get('type', None)
        if Type == "light":
            device = get_light(db, request.vars['id'])
            set_light(db, device, action)
        elif Type == "outlet":
            device = get_outlet(db, request.vars['id'])
            set_outlet(db, device, action)
    except Exception as error:
        response.flash = "Error turning {} {} {}".format(device['name'], Type, action)
    return sync()


# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
