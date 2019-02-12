#!/usr/bin/env python

import os
import sys


project_path = "/home/www-data/web2py"
app_path = "applications/garden"
db_path = "databases/storage.sqlite"


if os.getcwd() != project_path:
    sys.path.append(project_path)
    os.chdir(project_path)

from gluon import *

def action2bool(action):
    string = str(action).lower().strip()
    if action == True or action == 1 or string == "on" or string == "1": return True
    else: return False
