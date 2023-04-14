# This Python file uses the following encoding: utf-8
from pyrevit import revit, DB
from rpw.ui.forms import Alert

kolektor = DB.FilteredElementCollector(revit.doc).WhereElementIsNotElementType().WhereElementIsViewIndependent().OfCategory(DB.BuiltInCategory.OST_Walls).ToElements()
curtainWalls = []
n = 0
curtainWalls = [e for e in kolektor if revit.doc.GetElement(e.GetTypeId()).Kind == DB.WallKind.Curtain]
tits = "Disallow Joints for Curtain Walls"

with revit.Transaction(tits, revit.doc):
    for e in curtainWalls:
        n = n + 1
        if revit.doc.GetElement(e.Id):
            for i in range(2):
                DB.WallUtils.DisallowWallJoinAtEnd(e, i)
	# End Transaction
text = "Broj obrađenih zidova je : " + str(n) 
Alert(text, title=tits, header="Trolovi su uspešno obavili posao!")