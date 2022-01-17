# This Python file uses the following encoding: utf-8

from Autodesk.Revit.DB import Element, XYZ, CurveArray, ModelCurveArray, SpatialElementBoundaryOptions
from pyrevit import revit, DB, script, HOST_APP
from pyrevit.revit.db import query
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
from Autodesk.Revit import Exceptions, Creation


#kolektor
levels = DB.FilteredElementCollector(revit.doc).OfClass(DB.Level).ToElements()
rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
svaGledista = (DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewFamilyType)) 
floor_plan_type = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "Floor Plan"][1]
osnova = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).ToElements()
osnova = [find for find in osnova if find.Name == "±0.00"][0]
curtainWall= DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()
curtainDoor = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return(unique_list)


print(unique(curtainDoor))

with revit.Transaction("Šema vrata", revit.doc):
    for door in curtainDoor:
        name = query.get_name(door) 
        mark = query.get_mark(door)
        prefix = 'WD'
        tkVrata = name.startswith(prefix) 
        if tkVrata == True:
            pass
