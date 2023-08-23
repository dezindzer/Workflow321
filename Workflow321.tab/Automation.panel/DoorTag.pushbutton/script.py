# This Python file uses the following encoding: utf-8

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
from pyrevit.revit import doc, Transaction
from pyrevit import DB

# Generate a sequence of letters starting from 'A'
letter_sequence = iter(chr(i) for i in range(ord('A'), ord('Z')+1))

phases = doc.Phases
phase = phases[phases.Size - 1]
doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

for door in doors:
	if hasattr(door, "FromRoom") and str(phase.GetType()) == "Autodesk.Revit.DB.Phase":
		letter = next(letter_sequence)
		tag_parameter = door.LookupParameter("TAG VRATA")
		a = door.FromRoom[phase]
		b = door.ToRoom[phase]
		try:
			tagA_value = a.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()
		except:
			tagA_value = "X"
		try:
			tagB_value = b.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()
		except:
			tagB_value = "X"
	with Transaction("DoorTag", doc):
		try:
			tag_parameter.Set(tagA_value + "→" + tagB_value + "-" + letter)
		except:
			tag_parameter.Set(tagA_value + "→" + tagB_value + "-" + letter)