# This Python file uses the following encoding: utf-8
# inspiration and big part of the code is done by pyChilizer

### TO DO ###
### ISO filter
### list sorting by room number
### hide elements outside crop

from pyrevit import revit, DB, script, forms, HOST_APP
#from pyrevit.revit.db import query
from pyrevit.framework import List
from itertools import izip
from rpw import ui
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
#from Autodesk.Revit import Exceptions
import helper, math, units, sys

version = HOST_APP.version

def Canceled():
    forms.alert('User canceled the operation', title="Canceled", exitscript=True)

def GetCenterPoint(ele):
    bBox = ele.get_BoundingBox(None)
    return (bBox.Max + bBox.Min) / 2

output = script.get_output()
logger = script.get_logger()


# collector - choose by hand or all rooms
ops = ['All rooms', 'Choose rooms by hand']
cfgs = {'All rooms': { 'background': '0xFF55FF'}}
chosen_selection_method = forms.CommandSwitchWindow.show(ops, message='Select Option',  config=cfgs, recognize_access_key=False )

if chosen_selection_method == ops[0]:
    rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
elif chosen_selection_method == ops[1]:
    # use preselected elements, filtering rooms only
    rooms = helper.select_rooms_filter()
    if not rooms:
        forms.alert("You need to select at least one Room.", exitscript=True)
else:
    #chosen_selection_method.close()
    Canceled()

# collector other
osnove = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewPlan) 
osnova_dict = {v.Name: v for v in osnove if v.IsTemplate}
osnova_dict["<None>"] = None
plafon_dict = {v.Name: v for v in osnove if v.IsTemplate}
plafon_dict["<None>"] = None
pogledi = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewSection) 
viewsection_dict = {v.Name: v for v in pogledi if v.IsTemplate}
viewsection_dict["<None>"] = None

svaGledista = (DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewFamilyType)) 

titleblocks = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType()
tblock_dict = {'{}: {}'.format(tb.FamilyName, revit.query.get_name(tb)): tb for tb in titleblocks}

roomtagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_RoomTags).WhereElementIsElementType().ToElements()
roomtag_dict = {'{}: {}'.format(rt.FamilyName, revit.query.get_name(rt)): rt for rt in roomtagz}

floor_plan_type = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "Floor Plan"][1]
ceiling_plan_type = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "Ceiling Plan"][0]
elevation_type = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "Elevation"][1] 
allViews = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).ToElements()
firstView = allViews[1] # print(firstView)  print(DB.Element.Name.GetValue(firstView))
#print(DB.Element.Name.GetValue(firstView))
separator = " - "
view_scale = 50

# get units for Crop Offset variable
if units.is_metric(revit.doc):
    unit_sym = "Crop Offset [mm]"
    default_crop_offset = 350
else:
    unit_sym = "Crop Offset [decimal inches]"
    default_crop_offset = 9


components = [
    Label ("Select Titleblock"),
    ComboBox(name="tb", options=sorted(tblock_dict)), #default="Papir A2: A2 - SRB"),
    Label(unit_sym),
    TextBox("crop_offset", Text=str(default_crop_offset)),
    Separator(),
    Label("View Template for Floor Plans"),
    ComboBox(name="vt_floor_plans", options=sorted(osnova_dict)), #default="Osnova 1.50"),
    Label("View Template for Ceiling Plans"),
    ComboBox(name="vt_ceiling_plans", options=sorted(plafon_dict)), #default="Plafoni 1.50"),  
    Label("View Template for Elevations"),
    ComboBox(name="vt_elevs", options=sorted(viewsection_dict)),# default="Pogledi 1.50"),
    Separator(),
    Label ("Tag Rooms"),
    CheckBox(name="tag_rooms", checkbox_text="", default=False),
    Label ("Select Room Tag"),
    ComboBox(name="rt", options=sorted(roomtag_dict)), #default="CRE Room Tag 50: 3. Number, Area"),
    Label(""),
    Button("Ok")
]

form = FlexForm("View Settings", components)

viewSettings = form.show()
if viewSettings == True:
    sheet_number_start = 1
    chosen_crop_offset = units.correct_input_units(form.values["crop_offset"],  revit.doc)
    chosen_tb = tblock_dict[form.values["tb"]]
    chosen_vt_floor_plan = osnova_dict[form.values["vt_floor_plans"]]
    chosen_vt_ceiling_plan = plafon_dict[form.values["vt_ceiling_plans"]]
    chosen_vt_elevation = viewsection_dict[form.values["vt_elevs"]]
    #Room Tag
    chosen_roomTag = roomtag_dict[form.values["rt"]]
    chosen_tag_rooms = form.values["tag_rooms"]

    # approximate positions for viewports on an A2 sheet
    Xx = 0.8
    Yy = 0.4
    osnova_poz = DB.XYZ(-Xx, 1.5, 0)
    plafon_poz = DB.XYZ(Xx, 1.5, 0)
    pogledi_poz = [
        DB.XYZ(Xx, Yy, 0), #D
        DB.XYZ(-Xx, Xx, 0), #A
        DB.XYZ(Xx, Xx, 0), #B
        DB.XYZ(-Xx, Yy, 0), #C
    ]

    if not rooms:
        sys.exit()
    rmcnt = [rmc for rmc in rooms if rmc.Area > 0]
    #print(rmcnt)
    max_value = len(rmcnt)
    counter = 0

    with forms.ProgressBar(title='Creating Sheet ... ({value} of {max_value})') as pb:
        for eRoom in rmcnt:  
            counter = counter + 1
            imeSobe = eRoom.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
            for iS in imeSobe:
                if imeSobe == "Room":
                    imeSobe = ""
                    separator = " "
            level = eRoom.Level
            room_location = eRoom.Location.Point
            roomTagLocation = DB.UV(room_location.X, room_location.Y*1.035)
            roomId = DB.LinkElementId(eRoom.Id)
            
            with revit.TransactionGroup("Drawing on Sheet " + eRoom.Number, revit.doc):
            
                with revit.Transaction("Create Sheet " + eRoom.Number, revit.doc):
                    sheet = helper.create_sheet("04 - " + str(sheet_number_start), eRoom.Number + imeSobe, chosen_tb.Id)
                    katcrteza = sheet.LookupParameter("KATEGORIJA CRTEZA")
                    katcrteza.Set('04 Pogledi')
                                    
                with revit.Transaction("Create Room" + eRoom.Number, revit.doc):
                    # Create Floor Plan
                    osnova = DB.ViewPlan.Create(revit.doc, floor_plan_type.Id, level.Id)
                    osnova.Scale = view_scale
                    osnova.CropBoxActive = True
                    
                    # Create Ceiling Plan
                    plafon = DB.ViewPlan.Create(revit.doc, ceiling_plan_type.Id, level.Id)
                    plafon.Scale = view_scale
                    plafon.CropBoxActive = True

                    # Create Elevations
                    elevations_col = []
                    new_marker = DB.ElevationMarker.CreateElevationMarker(revit.doc, elevation_type.Id, room_location, view_scale)
                    elevation_count = ["D", "A", "B", "C"]
                    #revit.doc.Regenerate()
                    for i in range(4):
                        try:
                            elevation = new_marker.CreateElevation(revit.doc, firstView.Id, i)
                            elevation.Scale = view_scale
                            # Rename elevations
                            elevation_name = eRoom.Number + separator + imeSobe + " - " + elevation_count[i]
                            while helper.get_view(elevation_name):
                                elevation_name = elevation_name + " Copy 1"
                            
                            elevation.Name = elevation_name
                            elevations_col.append(elevation)
                            helper.set_anno_crop(elevation)
                        except:
                            #print("Greška u pravljenju elevationa. Proveriti da li postoje neophodne tipovi za elevation ( 1. Pogledi ) ili crtež osnove, ili da li su sve sobe zatvorene.")
                            print(eRoom.Number)
                
                # find crop box element (method with transactions, must be outside transaction)
                #crop_box_el = helper.find_crop_box(osnova)
                with revit.Transaction("Crop Plan", revit.doc):
                    room_boundaries = helper.get_room_bound(eRoom)
                    if room_boundaries:
                        # try offsetting boundaries (to include walls in plan view)
                        try:
                            offset_boundaries = room_boundaries.CreateViaOffset(
                                room_boundaries, chosen_crop_offset, DB.XYZ(0, 0, 1)
                            )
                            crop_shapeO = osnova.GetCropRegionShapeManager()
                            crop_shapeO.SetCropShape(offset_boundaries)
                            crop_shapeP = plafon.GetCropRegionShapeManager()
                            crop_shapeP.SetCropShape(offset_boundaries)
                            #revit.doc.Regenerate()
                        # for some shapes the offset will fail, then use BBox method
                        except:
                            #revit.doc.Regenerate()
                            # room bbox in this view
                            new_bbox = eRoom.get_BoundingBox(osnova)
                            osnova.CropBox = new_bbox
                            plafon.CropBox = new_bbox
                    # Rename Floor Plan
                    osnova_name = eRoom.Number + separator + imeSobe + " - Osnova"
                    plafon_name = eRoom.Number + separator + imeSobe + " - Plafon"

                    while helper.get_view(osnova_name):
                        osnova_name = osnova_name + " Copy 1"
                    osnova.Name = osnova_name
                    
                    while helper.get_view(plafon_name):
                        plafon_name = plafon_name + " Copy 1"
                    plafon.Name = plafon_name
                    
                    # set view template and crop
                    helper.set_anno_crop(osnova)
                    helper.set_anno_crop(plafon)
                    helper.apply_vt(osnova, chosen_vt_floor_plan)
                    helper.apply_vt(plafon, chosen_vt_ceiling_plan)
                    #revit.doc.Regenerate()

                with revit.Transaction("Add Views to Sheet", revit.doc):
                    # place view on sheet
                    postavi_osnovu = DB.Viewport.Create(revit.doc, sheet.Id, osnova.Id, osnova_poz)
                    postavi_plafon = DB.Viewport.Create(revit.doc, sheet.Id, plafon.Id, plafon_poz)

                    for el, pos, i in izip(elevations_col, pogledi_poz, elevation_count):
                        # place elevations
                        place_elevation = DB.Viewport.Create(revit.doc, sheet.Id, el.Id, pos)
                        # set viewport detail number
                        place_elevation.get_Parameter(DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER).Set(i)
                        #revit.doc.Regenerate()
                        
                with revit.Transaction("Room TAG", revit.doc):
        # ROOM TAG               
                    if chosen_tag_rooms == True:
                        try:
                            createRoomTag = revit.doc.Create.NewRoomTag(roomId, roomTagLocation, osnova.Id) 
                            createRoomTag.ChangeTypeId(chosen_roomTag.Id)	   
                        except:
                            forms.alert("Rooms not tagged.", title="Error")
                            pass
                        
                    #revit.doc.Regenerate()
            pb.update_progress(counter, max_value)
else:
    Canceled()