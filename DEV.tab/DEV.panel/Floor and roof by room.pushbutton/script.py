# This Python file uses the following encoding: utf-8
import clr
from Autodesk.Revit.DB import Element, XYZ, CurveArray, ModelCurveArray, SpatialElementBoundaryOptions
from pyrevit import revit, DB, script, HOST_APP
from pyrevit.revit.db import query
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
from Autodesk.Revit import Exceptions, Creation

def find_by_class_and_name(dbItem, namez):

    findBy = DB.FilteredElementCollector(revit.doc).OfClass(getattr(DB, dbItem)).ToElements()
    if findBy:
        return [find for find in findBy if find.Name == namez]
    else:
        return "Nor floor plan named ±0.00"
#print(find_by_class_and_name("Level", "±0.00"))
# print(find_by_class_and_name("Level", "±0.00"))
# print(find_by_class_and_name("RoofType", "600x600 Armstrong"))

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
    
    Label ("Place Roofs"),
    CheckBox(name="place_roof", checkbox_text="", default=True),
    Label ("Select Roof Type"),
    ComboBox(name="rf", options=sorted(roofType_dict)), #default="Sloped Glazing: 600x600 Armstrong"),
    Label("Select Roof Level"),
    ComboBox(name="rflvl", options=sorted(levels_roof_dict)), #default="+3.00: +3.00"),
    
    Separator(),
    
    Label ("Place Floor"),
    CheckBox(name="place_floor", checkbox_text="", default=False),
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

chosen_place_roof = form.values["place_roof"]
chosen_place_floor = form.values["place_floor"]

foot = 304.8 #jebem ih u usta imperialistička

# dodati if petlju ukoliko je sloped glazing
# offset od plafona
# naši paneli su FamilySymbol i to komplikuje stvari
# defaultRoofPanel = chosen_roof_type.get_Parameter(DB.BuiltInParameter.AUTO_PANEL)	
# print(defaultRoofPanel.AsElementId())
# getRoofPanelType = revit.doc.GetElement(defaultRoofPanel.AsElementId())
# print(getRoofPanelType)
# getThikness = getRoofPanelType.get_Parameter(DB.BuiltInParameter.CURTAIN_WALL_SYSPANEL_THICKNESS).AsDouble()
# print(getThikness)

#Crop
a = True
if a == True:
    chosen_crop_offset = -40
else:
    chosen_crop_offset = 0

with revit.Transaction("Create roof and floor", revit.doc):
    
    room_boundary_options = SpatialElementBoundaryOptions()
    for room in rooms:
        
        if room.Area > 0:
            room_level_id = room.Level
            room_boundary = room.GetBoundarySegments(room_boundary_options)[0]
            room_curves = CurveArray()
            roof_curves = DB.CurveLoop()
            normal = XYZ.BasisZ
                        
            for boundary_segment in room_boundary:
                crv = boundary_segment.GetCurve()
                room_curves.Append(crv)
                roof_curves.Append(crv)
                crvStart = crv.GetEndPoint(0)
                crvEnd = crv.GetEndPoint(1)
                inside = DB.XYZ(0, 0, 1)
                ccud = DB.CurveLoop.CreateViaOffset(roof_curves, chosen_crop_offset/foot, inside) #Create floor curve loop
                roofCurveArray = CurveArray() #Initialize the curve array
                for c in ccud: #Append the floor curves to the curve array
                    roofCurveArray.Append(c)
                
            if chosen_place_floor: #create floors
                newFlor = revit.doc.Create.NewFloor(room_curves, chosen_floor, chosen_floor_level, False, normal )
                flOffsetFromLvl = newFlor.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(0)
            
            if chosen_place_roof: #create roofs
                mcArray = clr.StrongBox[ModelCurveArray](ModelCurveArray())		
                newRof = revit.doc.Create.NewFootPrintRoof(roofCurveArray, chosen_roof_level, chosen_roof_type, mcArray)
                rfOffsetFromLvl = newRof.get_Parameter(DB.BuiltInParameter.ROOF_LEVEL_OFFSET_PARAM).Set(32/foot)
