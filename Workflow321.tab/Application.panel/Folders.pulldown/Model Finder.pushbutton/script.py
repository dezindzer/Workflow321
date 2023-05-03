# import libraries
import os
from System import Environment
# import pyrevit libraries
from pyrevit import forms, DB
from pyrevit.revit import doc

# try to open cache path
try:
    curdoc = DB.Document.PathName.GetValue(doc)
    curdir = curdoc.rsplit('\\',1)
    os.startfile(curdir[0])
except:
    try:
        guid = doc.WorksharingCentralGUID
        AppDataList = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData).split("\\")
        AppDataList.pop(-1)
        AppData = "\\".join(AppDataList)
        location =  AppData + "\\Local\\Autodesk\\Revit"
        os.startfile(location)
    except:
        forms.alert('Cannot find the file. This may be because the document is not yet saved to a location, or the path is not accessible to this script for opening.', title='Script cancelled')