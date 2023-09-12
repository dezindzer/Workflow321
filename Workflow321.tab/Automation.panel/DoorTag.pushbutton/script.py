from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
from pyrevit.revit import doc, Transaction
from pyrevit import DB

# Generate a sequence of letters starting from 'A'
letter_sequence = iter(chr(i) for i in range(ord('A'), ord('Z')+1))

# Collect all doors in the project
doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

# Create a dictionary to store doors grouped by room relationships
grouped_doors = {}
phases = doc.Phases
phase = phases[phases.Size - 1]
# Iterate through doors and group them by FromRoom and ToRoom relationships
for door in doors:
    if hasattr(door, "FromRoom"):
        FromRoom = door.FromRoom[phase]
        ToRoom = door.ToRoom[phase]
        room_key = (FromRoom, ToRoom)
        if room_key not in grouped_doors:
            grouped_doors[room_key] = []
        grouped_doors[room_key].append(door)

# Iterate through grouped doors and assign common tags
with Transaction("DoorTag", doc):
    for room_key, group in grouped_doors.items():
        letter = next(letter_sequence)
        tagA_value = doc.GetElement(room_key[0]).get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()
        tagB_value = doc.GetElement(room_key[1]).get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()
        common_tag = "{}-{}-{}".format(tagA_value, tagB_value, letter)
        for door in group:
            tag_parameter = door.LookupParameter("TAG VRATA")
            if tag_parameter:
                tag_parameter.Set(common_tag)
