# This Python file uses the following encoding: utf-8
# IMPORTS

import os
from pyrevit import HOST_APP

# VARIABLES
addinLocation = HOST_APP.app.CurrentUsersAddinsDataFolderPath

try:
    os.startfile(addinLocation)
except:
    os.startfile(addinLocation)