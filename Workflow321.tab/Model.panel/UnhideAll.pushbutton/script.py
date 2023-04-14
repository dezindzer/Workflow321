# This Python file uses the following encoding: utf-8
# idea comes from EF-Tools - simplified and using pyRevit lib
# second version is simplified using ChatGPT

from pyrevit import revit, DB

doc = revit.doc

with revit.Transaction("Unhide Everything", doc):
    doc.ActiveView.UnhideElements(DB.FilteredElementCollector(doc).WhereElementIsNotElementType().ToElementIds())