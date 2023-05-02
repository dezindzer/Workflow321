# This Python file uses the following encoding: utf-8

## TO DO ##
# Tag Doors in elevation views and offset the tag bellow the door

from pyrevit import revit, DB, forms
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
import sys

roomtagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_RoomTags).WhereElementIsElementType().ToElements()
roomtag_dict = {'{}: {}'.format(rt.FamilyName, revit.query.get_name(rt)): rt for rt in roomtagz}
paneltagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanelTags).WhereElementIsElementType().ToElements()
doortagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_DoorTags).WhereElementIsElementType().ToElements()

paneltag_dict = {'{}: {}'.format(pt.FamilyName, revit.query.get_name(pt)): pt for pt in paneltagz}
doorTag_dict = {'{}: {}'.format(dt.FamilyName, revit.query.get_name(dt)): dt for dt in doortagz}
elevationtagz = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanelTags).WhereElementIsElementType().ToElements()
elevationtag_dict = {'{}: {}'.format(et.FamilyName, revit.query.get_name(et)): et for et in elevationtagz}

# get all sheets
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

# define FlexForm components
components = [
    Label ("Tagging takes time, be patient!!!"),
    Separator(),
    CheckBox(name="tag_doors", checkbox_text="Tag Doors", default=True),
    ComboBox(name="dt", options=sorted(doorTag_dict)), #default="1.Paneli 1.50: Mark + Dimensions"),
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

# create and show FlexForm
form = FlexForm("Tag Options", components)
form.show()

# get chosen tags and options
chosen_doorTag = doorTag_dict[form.values["dt"]]
chosen_panelTag = paneltag_dict[form.values["pt"]]
chosen_elevationTag = paneltag_dict[form.values["et"]]
chosen_ceilingTag = paneltag_dict[form.values["cp"]]

### YesNO
#chosen_tag_rooms = form.values["tag_rooms"]
chosen_tag_door = form.values["tag_doors"]
chosen_tag_wall = form.values["tag_floorplanpanels"]
chosen_tag_elevation = form.values["tag_elevations"]
chosen_tag_ceiling = form.values["tag_ceilingpanels"]

###############

sheets = izborSheetova()
if not sheets:
	sys.exit()
max_value = len(sheets)

with forms.ProgressBar(title='Tagging Sheets ... ({value} of {max_value})', cancellable=True) as pb:
    counter = 0
    for sheet in sheets:
        viewports = sheet.GetAllViewports()
        with revit.Transaction("TAG! "+ str(counter) + " / " + str(max_value), revit.doc):
            for viewport in viewports:
                getViewport = revit.doc.GetElement(viewport)
                getViewId = getViewport.ViewId
                getView = revit.doc.GetElement(getViewId)
                testV = getView.ViewType
                testIfLegend = testV == testV.Legend
                testIfElevation = testV == testV.Elevation
                testIfFloorplan = testV == testV.FloorPlan
                testIfCeilingPlan = testV == testV.CeilingPlan
                
                # floor plan
                if testIfFloorplan == True:
                    wallInOsnova = DB.FilteredElementCollector(revit.doc, getView.Id).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
                    # wall tag in floorplan
                    if chosen_tag_wall == True:
                        for e in wallInOsnova: 
                            familyInstanceRef = DB.Reference(e)
                            wallPanelLocation = GetCenterPoint(e)  
                            g = e.FacingOrientation
                            wallX, wallY = g.Y, g.X
                            tagOrientationH, tagOrientationV = DB.TagOrientation.Horizontal, DB.TagOrientation.Vertical
                            
                            if wallX == 1.0 or wallX == -1.0:
                                createWallTag = DB.IndependentTag.Create(revit.doc, getView.Id, familyInstanceRef, False, DB.TagMode.TM_ADDBY_CATEGORY, tagOrientationH, wallPanelLocation)
                                createWallTag.ChangeTypeId(chosen_panelTag.Id)
                            elif wallY == 1.0 or wallY == -1.0:
                                createWallTag = DB.IndependentTag.Create(revit.doc, getView.Id, familyInstanceRef, False, DB.TagMode.TM_ADDBY_CATEGORY, tagOrientationV, wallPanelLocation)
                                createWallTag.ChangeTypeId(chosen_panelTag.Id)
                    else:
                        pass
                    doorInOsnova = DB.FilteredElementCollector(revit.doc, getView.Id).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_Doors).ToElements()
                    # door tag in floorplan
                    if chosen_tag_door == True:
                        for e in doorInOsnova: 
                            familyInstanceRef = DB.Reference(e)
                            doorPanelLocation = GetCenterPoint(e)
                            g = e.FacingOrientation
                            doorY =g.Y
                            tagOrientation = DB.TagOrientation.Horizontal if doorY == 1.0 or doorY == -1.0 else DB.TagOrientation.Vertical
                            createDoorTag = DB.IndependentTag.Create(revit.doc, getView.Id, familyInstanceRef, False, DB.TagMode.TM_ADDBY_CATEGORY, tagOrientation, doorPanelLocation)
                            createDoorTag.ChangeTypeId(chosen_doorTag.Id)
                    else:
                        pass
                # ceiling plan tag 
                if testIfCeilingPlan == True:
                    wallInRoof = DB.FilteredElementCollector(revit.doc, getView.Id).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
                    if chosen_tag_ceiling == True:
                        for e in wallInRoof: 
                                g = e.FacingOrientation
                                wallZ =g.Z
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
                # elevation plan
                if testIfElevation == True:
                    # wall tags in elevation views
                    if chosen_tag_elevation == True:
                        wallInElevation = DB.FilteredElementCollector(revit.doc, getView.Id).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
                        erd = getView.RightDirection 
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
                    else:
                        pass
                    
                    # door tags in elevation views
                    if chosen_tag_door == True:
                        for e in doorInOsnova: 
                            familyInstanceRef = DB.Reference(e)
                            doorPanelLocation = GetCenterPoint(e)
                            createDoorTag = DB.IndependentTag.Create(revit.doc, getView.Id, familyInstanceRef, False, DB.TagMode.TM_ADDBY_CATEGORY, DB.TagOrientation.Horizontal, doorPanelLocation)
                            createDoorTag.ChangeTypeId(chosen_doorTag.Id)	
                    else:
                        pass
                    
        pb.update_progress(counter, max_value)
        counter += 1