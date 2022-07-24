# This Python file uses the following encoding: utf-8

### TO DO ###
### tagging doors
### tagging of ceilin/roof panels

from pyrevit import revit, DB, script, forms, HOST_APP, forms
from pyrevit.forms import WPFWindow
from pyrevit.revit.db import query
from pyrevit.framework import List
from itertools import izip
from rpw import ui
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
from Autodesk.Revit import Exceptions
import sys, os, helper, re, math


roomtagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_RoomTags).WhereElementIsElementType().ToElements()
roomtag_dict = {'{}: {}'.format(rt.FamilyName, revit.query.get_name(rt)): rt for rt in roomtagz}
paneltagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanelTags).WhereElementIsElementType().ToElements()
paneltag_dict = {'{}: {}'.format(pt.FamilyName, revit.query.get_name(pt)): pt for pt in paneltagz}
elevationtagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanelTags).WhereElementIsElementType().ToElements()
elevationtag_dict = {'{}: {}'.format(et.FamilyName, revit.query.get_name(et)): et for et in elevationtagz}

all_sheets = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
sheetCat03 = [vt for vt in sheets if '03' in vt.LookupParameter("KATEGORIJA CRTEZA").AsString()]
sheetCat04 = [vt for vt in sheets if '04' in vt.LookupParameter("KATEGORIJA CRTEZA").AsString()]
options = sheetCat03+sheetCat04
sheet_dict = {'Pogledi i Osnove': options,'03 Osnove': sheetCat03, '04 Pogledi': sheetCat04, "All Sheets": sheets} #'03 Osnove': sheetCat03,
    
def izborSheetova():
    sheetsToTag = forms.SelectFromList.show(sheet_dict,multiselect=True,name_attr="Title",info_panel=False, group_selector_title="KATEGORIJA CRTEZA",default_group="04 Pogledi",button_name="Tag!", title="Choose Sheets To Tag")
    if not sheetsToTag:
        sys.exit(0)
    return sheetsToTag
def GetCenterPoint(ele):
    bBox = ele.get_BoundingBox(None)
    return (bBox.Max + bBox.Min) / 2

components = [
    #Label ("Select Room Tag"), ComboBox(name="rt", options=sorted(roomtag_dict)), #default="CRE Room Tag 50: 3. Number, Area"),
    #Label ("Tag Rooms"), CheckBox(name="tag_rooms", checkbox_text="", default=False),
    Label ("These Options Take Time!"),
    Separator(),
    CheckBox(name="tag_floorplanpanels", checkbox_text="Tag Floor Plan Panels", default=True),
    ComboBox(name="pt", options=sorted(paneltag_dict)), #default="1.Paneli 1.50: Mark + Dimensions"),
    Separator(),
    CheckBox(name="tag_ceilingpanels", checkbox_text="Tag Ceiling Plan Panels", default=True),
    ComboBox(name="cp", options=sorted(paneltag_dict)), #default="1.Paneli 1.50: Mark + Dimensions"),
    Separator(),
    CheckBox(name="tag_elevations", checkbox_text="Tag Elevations", default=True),
    ComboBox(name="et", options=sorted(paneltag_dict)), #default="1.Paneli 1.50: Mark + Dimensions"),
    Separator(),
    Label(""),
    Button("Ok")
]

form = FlexForm("Tag Options", components)
form.show()

#Tagovi
#chosen_roomTag = roomtag_dict[form.values["rt"]]
chosen_panelTag = paneltag_dict[form.values["pt"]]
chosen_elevationTag = paneltag_dict[form.values["et"]]
chosen_ceilingTag = paneltag_dict[form.values["cp"]]

### YesNO
#chosen_tag_rooms = form.values["tag_rooms"]
chosen_tag_wall = form.values["tag_floorplanpanels"]
chosen_tag_elevation = form.values["tag_elevations"]
chosen_tag_ceiling = form.values["tag_ceilingpanels"]

###############

sheets = izborSheetova()
if not sheets:
	sys.exit()
max_value = len(sheets)
counter = 0

with forms.ProgressBar(title='Tagging Sheets ... ({value} of {max_value})') as pb:
    #try:
        for sheet in sheets:
                counter = counter + 1
                viewports = sheet.GetAllViewports()
                with revit.TransactionGroup("TAG! "+ str(counter) + " / " + str(max_value), revit.doc):
                    for viewport in viewports:
                        getViewport = revit.doc.GetElement(viewport)
                        #print(getViewport.LookupParameter("View Name").AsString())
                        getViewId = getViewport.ViewId
                        #print(getViewId)
                        getView = revit.doc.GetElement(getViewId)
                        
                        testV = getView.ViewType
                        testIfLegend = testV == testV.Legend
                        testIfElevation = testV == testV.Elevation
                        testIfFloorplan = testV == testV.FloorPlan
                        testIfCeilingPlan = testV == testV.CeilingPlan
                        
                        # FloorPlan TAG 
                        if testIfFloorplan == True:
                            #print(getView.LookupParameter("View Name").AsString())     
                            #print("FloorPlan")
                            with revit.Transaction("TAG Floor Plan", revit.doc):
                                    
                                    wallInOsnova = DB.FilteredElementCollector(revit.doc, getView.Id).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
                                    if chosen_tag_wall == True:
                                        for e in wallInOsnova: 
                                                g = e.FacingOrientation
                                                wallX =g.Y
                                                wallY =g.X
                                                if wallX != 0:
                                                    tagOrientation = DB.TagOrientation.Horizontal
                                                if wallY != 0:
                                                    tagOrientation = DB.TagOrientation.Vertical
                                                else:
                                                    tagOrientation = DB.TagOrientation.Horizontal
                                                
                                                familyInstanceRef = DB.Reference(e)
                                                wallPanelLocation = GetCenterPoint(e)    
                                                createWallTag = DB.IndependentTag.Create(revit.doc, getView.Id, familyInstanceRef, False, DB.TagMode.TM_ADDBY_CATEGORY, tagOrientation, wallPanelLocation)
                                                createWallTag.ChangeTypeId(chosen_panelTag.Id)	   
                                        else:
                                            pass
                        # CeilingPlan TAG 
                        if testIfCeilingPlan == True:
                            #print(getView.LookupParameter("View Name").AsString())     
                            #print("CeilingPlan")
                            with revit.Transaction("TAG Ceiling Plan", revit.doc):
                                    wallInRoof = DB.FilteredElementCollector(revit.doc, getView.Id).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
                                    #wallInOsnova = DB.FilteredElementCollector(revit.doc, getView.Id).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
                                    if chosen_tag_ceiling == True:
                                        for e in wallInRoof: 
                                                g = e.FacingOrientation
                                                wallZ =g.Z
                                                #print(wallZ)
                                                wallX =g.Y
                                                wallY =g.X

                                                if wallZ == -1:
                                                    tagOrientation = DB.TagOrientation.Horizontal
                                                    familyInstanceRef = DB.Reference(e)
                                                    wallPanelLocation = GetCenterPoint(e)    
                                                    createWallTag = DB.IndependentTag.Create(revit.doc, getView.Id, familyInstanceRef, False, DB.TagMode.TM_ADDBY_CATEGORY, tagOrientation, wallPanelLocation)
                                                    createWallTag.ChangeTypeId(chosen_panelTag.Id)	   
                                        else:
                                            pass
                        # ELEVATION TAG
                        if testIfElevation == True:
                            # print(getView.LookupParameter("View Name").AsString())     
                            # print("Elevation")
                            with revit.Transaction("TAG Elevation Plan", revit.doc):
                                if chosen_tag_elevation == True:
                                    wallInElevation = DB.FilteredElementCollector(revit.doc, getView.Id).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
                                    erd = getView.RightDirection 
                                    #print(erd)
                                    #print(wallInElevation)
                                    for e in wallInElevation:
                                        d = e.FacingOrientation
                                        wallFrontFacing = d.Y
                                        erdX = erd.Y
                                        
                                        wallSideFacing = d.X
                                        erdY = erd.X
                                        
                                        testerdx = erdX == wallFrontFacing
                                        testerdy = erdY == wallSideFacing
                                        
                                        if testerdx != 0:
                                            familyInstanceRef = DB.Reference(e)
                                            wallPanelLocation = GetCenterPoint(e) 
                                            createElevationTag = DB.IndependentTag.Create(revit.doc, getView.Id, familyInstanceRef, False, DB.TagMode.TM_ADDBY_CATEGORY, DB.TagOrientation.Horizontal, wallPanelLocation)
                                            createElevationTag.ChangeTypeId(chosen_elevationTag.Id)
                                        if testerdy != 1:
                                            familyInstanceRef = DB.Reference(e)
                                            wallPanelLocation = GetCenterPoint(e) 
                                            createElevationTag = DB.IndependentTag.Create(revit.doc, getView.Id, familyInstanceRef, False, DB.TagMode.TM_ADDBY_CATEGORY, DB.TagOrientation.Horizontal, wallPanelLocation)
                                            createElevationTag.ChangeTypeId(chosen_elevationTag.Id)
                        # if testIfLegend == True:
                        #     print(getView.LookupParameter("View Name").AsString())     
                        #     print("Legend")
                        
                        # ROOM TAG               
                            # if chosen_tag_rooms == True:
                            #     for e in wallInOsnova:  
                            #         createRoomTag = revit.doc.Create.NewRoomTag(roomId, roomTagLocation, getView.Id) 
                            #         createRoomTag.ChangeTypeId(chosen_roomTag.Id)	   
                            #     else:
                            #         pass
                            
                    #revit.doc.Regenerate()
pb.update_progress(counter, max_value)
    #except:
    #    forms.alert("Cancelled or Error", ok=True, exitscript=True)