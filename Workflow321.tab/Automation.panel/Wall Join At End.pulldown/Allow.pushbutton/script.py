# This Python file uses the following encoding: utf-8
from pyrevit import revit, DB, forms

kolektor = DB.FilteredElementCollector(revit.doc).WhereElementIsNotElementType().WhereElementIsViewIndependent().OfCategory(DB.BuiltInCategory.OST_Walls).ToElements()
curtainWalls = []
n = 0
curtainWalls = [e for e in kolektor if revit.doc.GetElement(e.GetTypeId()).Kind == DB.WallKind.Curtain]
title = "Disallow Joints for Curtain Walls"

with revit.Transaction(title, revit.doc):
    for e in curtainWalls:
        n = n + 1
        if revit.doc.GetElement(e.Id):
            for i in range(2):
                DB.WallUtils.AllowWallJoinAtEnd(e, i)
	# End Transaction
forms.alert(title=title, msg="All "+ str(n)+" wall ends joined", sub_msg="The minions have successfully done their job!", warn_icon=False)