# This Python file uses the following encoding: utf-8

from Autodesk.Revit.DB import Element, XYZ, CurveArray, ModelCurveArray, SpatialElementBoundaryOptions
from pyrevit import revit, DB, script, HOST_APP
from pyrevit.revit.db import query
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
from Autodesk.Revit import Exceptions, Creation


grids = DB.FilteredElementCollector(revit.doc).OfClass(DB.CurtainGrid).ToElements()

#grids = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainGridsWall).WhereElementIsNotElementType().ToElements()
print(grids)

for e in grids:
    a = e.GetVGridLineIds()
    print(a)	
