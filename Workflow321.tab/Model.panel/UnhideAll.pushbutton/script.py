# This Python file uses the following encoding: utf-8
# idea comes from EF-Tools - simplified and using pyRevit lib

from pyrevit import revit, DB
from pyrevit.framework import List

doc = revit.doc

all_elements = DB.FilteredElementCollector(doc).WhereElementIsNotElementType().ToElementIds()
unhide_elements = List[DB.ElementId](all_elements)

with revit.Transaction("Unhide Everything", doc):
    doc.ActiveView.UnhideElements(unhide_elements)
