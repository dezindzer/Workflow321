# This Python file uses the following encoding: utf-8

from pyrevit import revit, DB
from rpw.ui.forms import Alert

kolektor = DB.FilteredElementCollector(revit.doc).WhereElementIsNotElementType().WhereElementIsViewIndependent().OfCategory(DB.BuiltInCategory.OST_Walls).ToElements()
curtainWalls = []
n = 0

for e in kolektor:
	try:
		elementType = revit.doc.GetElement(e.GetTypeId())
		if elementType.Kind == DB.WallKind.Curtain:
			curtainWalls.append(e)
			n = n + 1
	except:
		print("not curtain wall")	

text = "Broj obrađenih zidova je : " + str(n) 
tits = "Disallow Joints for Curtain Walls"

Alert(text, title=tits, header="Trolovi su uspešno obavili posao!")

with revit.Transaction(tits, revit.doc):
	for e in curtainWalls:
		try:
			DB.WallUtils.DisallowWallJoinAtEnd(e, 0)
			DB.WallUtils.DisallowWallJoinAtEnd(e, 1)
		except:
			print("Fail")
	# End Transaction