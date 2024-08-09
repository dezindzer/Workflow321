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
        location =  AppData + "\\Local\\Autodesk\\Revit\\PacCache"
        os.startfile(location)
    except:
        forms.alert('Cannot find the folder. This may be because you dont have Revit Accelerator Installed.', title='Script cancelled')
        
    