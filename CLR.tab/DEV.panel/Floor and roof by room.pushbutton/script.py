# This Python file uses the following encoding: utf-8

from pyrevit import revit, DB, script, forms, HOST_APP
from pyrevit.revit.db import query
from pyrevit.framework import List
from itertools import izip
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
from Autodesk.Revit import Exceptions
import helper

def find_by_class_and_name(dbItem, namez):
    # from given family doc, return Ref. Level reference plane
    findBy = DB.FilteredElementCollector(revit.doc).OfClass(getattr(DB, dbItem)).ToElements()
    return [find for find in findBy if find.Name == namez]

# kolektori
rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
roofs = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Roofs).WhereElementIsNotElementType().ToElements()
#print(roofs)

floors = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
level = DB.FilteredElementCollector(revit.doc).OfClass(DB.Level).WhereElementIsNotElementType().ToElements()

a = DB.FilteredElementCollector(revit.doc).OfClass(DB.RoofType).ToElements()
print(a)

#print(find_by_class_and_name("Level", "±0.00"))
#print(find_by_class_and_name("RoofType", "600x600 Armstrong"))




# test = level.Name == "±0.00"

# svaGledista = (DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewFamilyType)) 

# separator = " - "

# get units for Crop Offset variable
# default_crop_offset = 0

# for room in rooms:  
#     if room.Area > 0:
#         imeSobe = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
#         for iS in imeSobe:
#             if imeSobe == "Room":
#                 imeSobe = ""
#                 separator = " "
#         level = room.Level
#         room_location = room.Location.Point
#         roomTagLocation = DB.UV(room_location.X, room_location.Y*1.035)
#         roomId = DB.LinkElementId(room.Id)

#         with revit.TransactionGroup("Drawing on Sheet " + room.Number, revit.doc):
       
    
#             with revit.Transaction("Create Room and tag all" + room.Number, revit.doc):
#                 # Create Floor Plan
#                 osnova = DB.ViewPlan.Create(revit.doc, floor_plan_type.Id, level.Id)
#                 osnova.Scale = view_scale

#                 # Create Ceiling Plan
#                 plafon = DB.ViewPlan.Create(revit.doc, ceiling_plan_type.Id, level.Id)
#                 plafon.Scale = view_scale
#                 # Create Elevations
#                 revit.doc.Regenerate()

#             # find crop box element (method with transactions, must be outside transaction)
#             crop_box_el = helper.find_crop_box(osnova)

#             with revit.Transaction("Crop Plan", revit.doc):
#                 osnova.CropBoxActive = True
#                 plafon.CropBoxActive = True
#                 revit.doc.Regenerate()

#                 room_boundaries = helper.get_room_bound(room)
#                 if room_boundaries:
#                     # try offsetting boundaries (to include walls in plan view)
#                     try:
#                         offset_boundaries = room_boundaries.CreateViaOffset(
#                             room_boundaries, chosen_crop_offset, DB.XYZ(0, 0, 1)
#                         )
#                         crop_shapeO = osnova.GetCropRegionShapeManager()
#                         crop_shapeO.SetCropShape(offset_boundaries)
#                         crop_shapeP = plafon.GetCropRegionShapeManager()
#                         crop_shapeP.SetCropShape(offset_boundaries)
#                         revit.doc.Regenerate()
#                     # for some shapes the offset will fail, then use BBox method
#                     except:
#                         revit.doc.Regenerate()
#                         # room bbox in this view
#                         new_bbox = room.get_BoundingBox(osnova)
#                         osnova.CropBox = new_bbox

#                 # Rename Floor Plan
#                 osnova_name = room.Number + separator + imeSobe + " - Osnova"
#                 plafon_name = room.Number + separator + imeSobe + " - Plafon"

#                 while helper.get_view(osnova_name):
#                     osnova_name = osnova_name + " Copy 1"
#                 osnova.Name = osnova_name
                
#                 while helper.get_view(plafon_name):
#                     plafon_name = plafon_name + " Copy 1"
#                 plafon.Name = plafon_name
                
#                 # set view template and crop
#                 helper.set_anno_crop(osnova)
#                 helper.set_anno_crop(plafon)
#                 helper.apply_vt(osnova, chosen_vt_floor_plan)
#                 helper.apply_vt(plafon, chosen_vt_ceiling_plan)


