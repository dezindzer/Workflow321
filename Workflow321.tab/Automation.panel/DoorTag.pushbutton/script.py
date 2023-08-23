# This Python file uses the following encoding: utf-8

from pyrevit import revit, DB
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, SpatialElementBoundaryOptions
from Autodesk.Revit.DB.Architecture import Room
from pyrevit.revit import doc, Transaction, UI

# Get the current Revit document

# # Function to collect all doors in a room
# def get_doors_in_room(room):
#     doors = []

#     # Get the bounding elements of the room
#     boundary_options = SpatialElementBoundaryOptions()
#     print(boundary_options)
#     boundary_elements = room.GetBoundarySegments(boundary_options)

#     # Loop through boundary elements to find doors
#     for boundary_element in boundary_elements:
#         for segment in boundary_element:
#             element = doc.GetElement(segment.ElementId)
#             if element.Category.Id == BuiltInCategory.OST_Doors:
#                 doors.append(element)
#     print(doors)
#     return doors

# # Use FilteredElementCollector to get all rooms
# room_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
# all_rooms = list(room_collector)

# # Generate a sequence of letters starting from 'A'
# letter_sequence = iter(chr(i) for i in range(ord('A'), ord('Z')+1))

# # Start a transaction to make changes
# transaction = Transaction(doc, "Update Door Tags")
# transaction.Start()

# # Populate the parameter for each door in each room
# for room in all_rooms:
#     doors_in_room = get_doors_in_room(room)
#     print(bool(doors_in_room))
#     if doors_in_room:
#         room_number = room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()
#         for door in doors_in_room:
#             letter = next(letter_sequence)
#             tag_parameter = door.LookupParameter("TAG VRATA")
#             tag_value = "{}-{}".format(room_number, letter)
#             try:
#                 transaction_status = tag_parameter.Set(tag_value)
#                 if transaction_status != DB.TransactionStatus.Committed:
#                     print("Failed to set tag value for door:", door.Id)
#             except Exception as e:
#                 print("Error setting tag value for door:", door.Id)
#                 print(str(e))

# # Commit the transaction
# transaction.Commit()

# phases = doc.Phases

# phase = phases[phases.Size - 1]

# # Function to get the room from the "From Room" or "To Room" parameter of a door
# def get_door_room(door):
#     #to_room = door.get_Parameter(DB.BuiltInParameter.DOOR_TO_ROOM_PARAM).AsElementId()
    
#     from_room_id = door.FromRoom
#     to_room_id = door.ToRoom
#     try:
#         froom = door.FromRoom[phase].Id
#     except:
#         froom = -1
#     try:
#         troom = door.ToRoom[phase].Id
#     except:
#         troom = -1
#     UI.TaskDialog.Show("Revit","%s, %s" %(froom, troom))

#     if not from_room_id and not to_room_id:
#         return None
    
#     if from_room_id:
#         return doc.GetElement(from_room_id)
#     else:
#         return doc.GetElement(to_room_id)

# # Function to collect all doors in a room
# def get_doors_in_room(room):
#     doors = []

#     door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType()
#     for door in door_collector:
#         door_room = get_door_room(door)
#         if door_room and door_room.Id == room.Id:
#             doors.append(door)
    
#     return doors

# # Use FilteredElementCollector to get all rooms
# room_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
# all_rooms = list(room_collector)

# # Generate a sequence of letters starting from 'A'
# letter_sequence = iter(chr(i) for i in range(ord('A'), ord('Z')+1))

# # Start a transaction to make changes
# with Transaction("Isolate flipped doors in current view", doc):
# 	# Populate the parameter for each door in each room
# 	for room in all_rooms:
# 		doors_in_room = get_doors_in_room(room)
		
# 		if doors_in_room:
# 			room_number = room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()
# 			for door in doors_in_room:
# 				letter = next(letter_sequence)
# 				tag_parameter = door.LookupParameter("TAG VRATA")
# 				if tag_parameter:
# 					tag_value = "{}-{}".format(room_number, letter)
# 					try:
# 						transaction_status = tag_parameter.Set(tag_value)
# 						if transaction_status != DB.TransactionStatus.Committed:
# 							print("Failed to set tag value for door:", door.Id)
# 					except Exception as e:
# 						print("Error setting tag value for door:", door.Id)
# 						print(str(e))


# This Python file uses the following encoding: utf-8

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

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
	with revit.Transaction("DoorTag", revit.doc):
		try:
			tag_parameter.Set(tagA_value + "→" + tagB_value + "-" + letter)
		except:
			tag_parameter.Set(tagA_value + "→" + tagB_value + "-" + letter)