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
