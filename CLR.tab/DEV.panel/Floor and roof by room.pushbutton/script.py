# This Python file uses the following encoding: utf-8

from pyrevit import revit, DB, script, HOST_APP
from pyrevit.revit.db import query
from pyrevit.framework import List
from itertools import izip
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
from Autodesk.Revit import Exceptions
import helper

def find_by_class_and_name(dbItem, namez):

    findBy = DB.FilteredElementCollector(revit.doc).OfClass(getattr(DB, dbItem)).ToElements()
    if findBy:
        return [find for find in findBy if find.Name == namez]
    else:
        return "Nor floor plan named ±0.00"
#print(find_by_class_and_name("Level", "±0.00"))


#kolektor

levels = DB.FilteredElementCollector(revit.doc).OfClass(DB.Level).ToElements()
roofTypes = DB.FilteredElementCollector(revit.doc).OfClass(DB.RoofType).ToElements()
floors = DB.FilteredElementCollector(revit.doc).OfClass(DB.FloorType).ToElements()

rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
roofs = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Roofs).WhereElementIsNotElementType().ToElements()
svaGledista = (DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewFamilyType)) 
floor_plan_type = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "Floor Plan"][1]

osnova = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).ToElements()
osnova = [find for find in osnova if find.Name == "±0.00"][0]

#dict
roofType_dict = {'{}: {}'.format(rf.FamilyName, revit.query.get_name(rf)): rf for rf in roofTypes}
levels_roof_dict = {'{}: {}'.format(lvl.Name, revit.query.get_name(lvl)): lvl for lvl in levels}
levels_floor_dict = {'{}: {}'.format(lvl.Name, revit.query.get_name(lvl)): lvl for lvl in levels}
floors_dict = {'{}: {}'.format(fl.FamilyName, revit.query.get_name(fl)): fl for fl in floors}

#form
components = [
    Label ("Select Roof Type"),
    ComboBox(name="rf", options=sorted(roofType_dict), default="Sloped Glazing: 600x600 Armstrong"),
    Label("Select Roof Level"),
    ComboBox(name="rflvl", options=sorted(levels_roof_dict), default="+3.00: +3.00"),
    Separator(),
    Label("Select Floor Type"),
    ComboBox(name="fl", options=sorted(floors_dict), default="Floor: Clean room floor"),
    Label("Select Floor Level"),
    ComboBox(name="fllvl", options=sorted(levels_floor_dict), default="±0.00: ±0.00"),
    Separator(),
    Label(""),
    Button("Ok")
]
form = FlexForm("Settings", components)
form.show()

chosen_roof_type = roofType_dict[form.values["rf"]]
chosen_floor = floors_dict[form.values["fl"]]
chosen_roof_level = levels_roof_dict[form.values["rflvl"]]
chosen_floor_level = levels_floor_dict[form.values["fllvl"]]

#Crop
a = True
if a == True:
    chosen_crop_offset = 40
else:
    chosen_crop_offset = 0


def get_room_bound(r):
    room_boundaries = DB.CurveArray()
    modelCurveArray = DB.ModelCurveArray()
    # get room boundary segments
    room_segments = r.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
    # iterate through loops of segments and add them to the array
    outer_loop = room_segments[0]
    # for curve in outer_loop:
    curve_loop = [s.GetCurve() for s in outer_loop]
    open_ends = helper.get_open_ends(curve_loop)
    if open_ends:
        return None
    for curve in curve_loop:
        # try:
        room_boundaries.Append(curve)
        modelCurveArray.Append(curve)
        # except Exceptions.ArgumentException:
        #     print (curve)
    return room_boundaries, modelCurveArray

footprint = DB.Create.NewCurveArray()



with revit.Transaction("Create roof and floor", revit.doc):
    for room in rooms:
        room_boundaries = get_room_bound(room)
        roof = revit.doc.Create.NewFootPrintRoof(room_boundaries[0], chosen_roof_level, chosen_roof_type, room_boundaries[1])

        if room_boundaries:
            # try offsetting boundaries (to include walls in plan view)
            #try:
            #footPrint = room_boundaries.CreateViaOffset(room_boundaries, chosen_crop_offset, DB.XYZ(0, 0, 1))


            revit.doc.Regenerate()
            # for some shapes the offset will fail, then use BBox method
        else: #except:
            revit.doc.Regenerate()
            # room bbox in this view
            # footPrint = room.get_BoundingBox(osnova)
            # roof = revit.doc.Create.NewFootPrintRoof(footPrint, chosen_roof_level, chosen_roof_type, footPrint)
            pass 
        revit.doc.Regenerate()


# roof = DB.Create.NewFootPrintRoof(footPrint, level, type, mcArray)

# public FootPrintRoof NewFootPrintRoof(
# 	CurveArray footPrint,
# 	Level level,
# 	RoofType roofType,
# 	out ModelCurveArray footPrintToModelCurvesMapping
# )
CurveArray = ""
#floor = DB.NewFloor(CurveArray, chosen_floor, chosen_floor_level, True)

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


