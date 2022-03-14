# This Python file uses the following encoding: utf-8

### TO DO ###
### dodati filter za ISO
### sortirati listu prema broju sobe
### tagovanje vrata
### tagovanje plafonskih panela

from pyrevit import revit, DB, script, forms, HOST_APP, forms
from pyrevit.revit.db import query
from pyrevit.framework import List
from itertools import izip
from rpw import ui
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
from Autodesk.Revit import Exceptions
import math
import sys
import helper
import re
from pyrevit.forms import WPFWindow


count=1

all_sheets = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

sheetCat03 = [vt for vt in sheets if '03' in vt.LookupParameter("KATEGORIJA CRTEZA").AsString()]
sheetCat04 = [vt for vt in sheets if '04' in vt.LookupParameter("KATEGORIJA CRTEZA").AsString()]
options = sheetCat03+sheetCat04

ops = {'Pogledi i Osnove': options, '04 Pogledi': sheetCat04, "All Sheets": sheets} #'03 Osnove': sheetCat03,
res = forms.SelectFromList.show(ops,multiselect=True,name_attr="Title",group_selector_title="KATEGORIJA CRTEZA",button_name="Tag!", title="Choose Sheets To Tag")


def GetCenterPoint(ele):
    bBox = ele.get_BoundingBox(None)
    return (bBox.Max + bBox.Min) / 2

# # kolektori
# rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
# osnove = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewPlan) 
# osnova_dict = {v.Name: v for v in osnove if v.IsTemplate}
# osnova_dict["<None>"] = None
# plafon_dict = {v.Name: v for v in osnove if v.IsTemplate}
# plafon_dict["<None>"] = None
# pogledi = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewSection) 
# viewsection_dict = {v.Name: v for v in pogledi if v.IsTemplate}
# viewsection_dict["<None>"] = None

# svaGledista = (DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewFamilyType)) 

# titleblocks = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType()
# tblock_dict = {'{}: {}'.format(tb.FamilyName, revit.query.get_name(tb)): tb for tb in titleblocks}
    
# roomtagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_RoomTags).WhereElementIsElementType().ToElements()
# roomtag_dict = {'{}: {}'.format(rt.FamilyName, revit.query.get_name(rt)): rt for rt in roomtagz}

# paneltagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanelTags).WhereElementIsElementType().ToElements()
# paneltag_dict = {'{}: {}'.format(pt.FamilyName, revit.query.get_name(pt)): pt for pt in paneltagz}

# elevationtagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanelTags).WhereElementIsElementType().ToElements()
# elevationtag_dict = {'{}: {}'.format(et.FamilyName, revit.query.get_name(et)): et for et in elevationtagz}

# floor_plan_type = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "Floor Plan"][1]
# ceiling_plan_type = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "Ceiling Plan"][0]
# elevation_type = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "Elevation"][1] 
# allViews = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).ToElements()
# firstView = allViews[1] # print(firstView)  print(DB.Element.Name.GetValue(firstView))
# separator = " - "
# view_scale = 50

# # get units for Crop Offset variable
# display_units = DB.Document.GetUnits(revit.doc).GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits
# if helper.is_metric(revit.doc):
#     unit_sym = "Crop Offset [mm]"
#     default_crop_offset = 350
# else:
#     unit_sym = "Crop Offset [decimal inches]"
#     default_crop_offset = 9.0

# components = [
#     Label ("Select Titleblock"),
#     ComboBox(name="tb", options=sorted(tblock_dict), default="Papir A2: A2 - SRB"),
#     Label(unit_sym),
#     TextBox("crop_offset", Text=str(default_crop_offset)),
#     Separator(),
#     Label("View Template for Floor Plans"),
#     ComboBox(name="vt_floor_plans", options=sorted(osnova_dict), default="Osnova 1.50"),
#     Label("View Template for Ceiling Plans"),
#     ComboBox(name="vt_ceiling_plans", options=sorted(plafon_dict), default="Plafoni 1.50"),  
#     Label("View Template for Elevations"),
#     ComboBox(name="vt_elevs", options=sorted(viewsection_dict), default="Pogledi 1.50"),
#     Label ("Select Room Tag"),
#     ComboBox(name="rt", options=sorted(roomtag_dict)), #default="CRE Room Tag 50: 3. Number, Area"),
#     Label ("Select FloorPlan Panel Tag"),
#     ComboBox(name="pt", options=sorted(paneltag_dict)), #default="1.Paneli 1.50: Mark + Dimensions"),
#     Label ("Select Elevation Panel Tag"),
#     ComboBox(name="et", options=sorted(elevationtag_dict)), #default="1.Paneli 1.50: Mark + Dimensions"),
#     Separator(),
#     Label ("Tag Rooms"),
#     CheckBox(name="tag_rooms", checkbox_text="", default=False),
#     Label ("Tag Walls"),
#     CheckBox(name="tag_walls", checkbox_text="This option takes time", default=False),
#     Label ("Tag Elevations"),
#     CheckBox(name="tag_elevations", checkbox_text="This option takes time", default=False),
#     Separator(),
#     Label(""),
#     Button("Ok")
# ]

# form = FlexForm("View Settings", components)
# form.show()
# sheet_number_start = 1
# chosen_crop_offset = helper.correct_input_units(form.values["crop_offset"])

# chosen_tb = tblock_dict[form.values["tb"]]
# chosen_vt_floor_plan = osnova_dict[form.values["vt_floor_plans"]]
# chosen_vt_ceiling_plan = plafon_dict[form.values["vt_ceiling_plans"]]
# chosen_vt_elevation = viewsection_dict[form.values["vt_elevs"]]

# #Tagovi
# chosen_roomTag = roomtag_dict[form.values["rt"]]
# chosen_panelTag = paneltag_dict[form.values["pt"]]
# chosen_elevationTag = paneltag_dict[form.values["et"]]
# ### YesNO
# chosen_tag_rooms = form.values["tag_rooms"]
# chosen_tag_wall = form.values["tag_walls"]
# chosen_tag_elevation = form.values["tag_elevations"]

# # approximate positions for viewports on an A2 sheet
# Xx = 0.8
# Yy = 0.4
# osnova_poz = DB.XYZ(-Xx, 1.5, 0)
# plafon_poz = DB.XYZ(Xx, 1.5, 0)
# pogledi_poz = [
#     DB.XYZ(Xx, Yy, 0), #D
#     DB.XYZ(-Xx, Xx, 0), #A
#     DB.XYZ(Xx, Xx, 0), #B
#     DB.XYZ(-Xx, Yy, 0), #C
# ]


for e in res:
    views = e.GetAllViewports()
    for view in views:
        getViewport = revit.doc.GetElement(view)
        print(getViewport.LookupParameter("View Name").AsString())
        getViewId = getViewport.ViewId
        print(getViewId)
        getView = revit.doc.GetElement(getViewId)
        print(getView.LookupParameter("View Name").AsString())

        #print(getView.get_Parameter(DB.BuiltInParameter.OST_ViewportLabel).AsString())
    
    
    # with revit.Transaction("TAG", revit.doc):
    #     # WALL TAG 
    #     wallInOsnova = DB.FilteredElementCollector(revit.doc, osnova.Id).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
    #     if chosen_tag_wall == True:
    #         for e in wallInOsnova: 
    #                 g = e.FacingOrientation
    #                 wallX =g.Y
    #                 wallY =g.X
    #                 if wallX != 0:
    #                     tagOrientation = DB.TagOrientation.Horizontal
    #                 if wallY != 0:
    #                     tagOrientation = DB.TagOrientation.Vertical
    #                 else:
    #                     tagOrientation = DB.TagOrientation.Horizontal
                    
    #                 familyInstanceRef = DB.Reference(e)
    #                 wallPanelLocation = GetCenterPoint(e)    
    #                 createWallTag = DB.IndependentTag.Create(revit.doc, osnova.Id, familyInstanceRef, False, DB.TagMode.TM_ADDBY_CATEGORY, tagOrientation, wallPanelLocation)
    #                 createWallTag.ChangeTypeId(chosen_panelTag.Id)	   
    #         else:
    #             pass  
    #     # ROOM TAG               
    #     if chosen_tag_rooms == True:
    #         for e in wallInOsnova:  
    #             createRoomTag = revit.doc.Create.NewRoomTag(roomId, roomTagLocation, osnova.Id) 
    #             createRoomTag.ChangeTypeId(chosen_roomTag.Id)	   
    #         else:
    #             pass
        
    #     revit.doc.Regenerate()