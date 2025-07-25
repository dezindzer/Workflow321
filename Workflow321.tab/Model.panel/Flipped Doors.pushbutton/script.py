# This Python file uses the following encoding: utf-8
#to do:
#change 3D view type

from pyrevit import revit, DB
from pyrevit.revit.db import query
from pyrevit.framework import List
from Autodesk.Revit.DB import Element   #ne brisati
from rpw.ui.forms import Alert
from pyrevit.revit import doc, Transaction

curview = revit.active_view

def apply_vt(v, vt):
    if vt:
        v.ViewTemplateId = vt.Id
    return

def GetCenterPoint(ele):
    bBox = ele.get_BoundingBox(None)
    return (bBox.Max + bBox.Min) / 2

tits = "Flipped Doors"
pogledi3D = DB.FilteredElementCollector(doc).OfClass(DB.View3D)

viewTemplate = {v.Name: v for v in pogledi3D if v.IsTemplate}

first3Delement = pogledi3D.ToElements()
first3DView = first3Delement[0]

#FamSymbol = ToElements()

FamSymbol = next(fs for fs in DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol).WhereElementIsElementType() if fs.FamilyName == "AAAA")


print(FamSymbol)

doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType()
flippedId = List[DB.ElementId]()
familyType = next(vt for vt in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).WhereElementIsElementType() if vt.FamilyName == "3D View" and Element.Name.__get__(vt) == "3D View - Flipped Doors")
    # have to use the imported Element otherwise - AttributeError - occurs

with Transaction(tits, doc):
    #create a view template if it does not exist already
                if viewTemplate:
                    viewTemplateFlip = viewTemplate[tits]
                else:   
                    first3DView.Scale = 25
                    create3DTemplate = first3DView.CreateViewTemplate()
                    create3DTemplate.Name = tits
                    viewTemplateFlip = create3DTemplate
                for door in doors:
                    door_name = query.get_name(door) 
                    door_mark = query.get_mark(door)
                    revitID = DB.Element.Id.GetValue(door)
                    if door_mark == "" or door_mark == None:
                        door_mark = ""
                    else:
                        door_mark = " Mark " + door_mark + " - "
                    #print(door) 
                    prefix = 'WD'
                    tkVrata = door_name.startswith(prefix) 
                    if tkVrata == True:
                        flips = []
                        flip = 1 if door.HandFlipped else 0
                        face = 1 if door.FacingFlipped else 0	
                        flips.append(flip+face == 1)
                        if flips[0] == True:
                            for view in enumerate(flips):
                                flippedId.Add(revitID)
                                wallHost= door.Host
                                view = DB.View3D.CreateIsometric(doc, familyType.Id)
                                view.SaveOrientationAndLock()
                                doorPanelLocation = GetCenterPoint(door)
                                familyInstanceRef = DB.Reference(door)
                                tagOrientation = DB.TagOrientation.AnyModelDirection
                                print(doorPanelLocation)
                                locationZero = DB.XYZ(2.296120953, 0.997921127, 1.310517528)
                                createDoorTag = DB.IndependentTag.Create(revit.doc, view.Id, familyInstanceRef, True, DB.TagMode.TM_ADDBY_CATEGORY, tagOrientation, doorPanelLocation)
                                createDoorTag = DB.IndependentTag.Create(revit.doc, FamSymbol.Id ,view.Id, familyInstanceRef, True,  tagOrientation, doorPanelLocation)
                                print(createDoorTag)
                                
                                apply_vt(view, viewTemplateFlip)
                                BoundingBoxXYZ = door.get_BoundingBox(view)                
                                view.SetSectionBox(BoundingBoxXYZ)
                                viewName = door_name + " - " + door_mark + " ID " + str(revitID)
                                #loop za proveru da li ime vec postoji, ako da, napravi novi sa Copy 1 tagom
                                while query.get_view_by_name(viewName):
                                    viewName = viewName + " Copy 1"
                                view.Name = viewName
counter=len(flippedId)
if counter>0:
    Alert("Found elements will be isolated.\n \nViews are created with the \"3D Views (Flipped Doors)\" type. \nYou can find them in the project browser!", title=tits, header = str(counter) + " flipped doors were found.")
    with Transaction("Isolate flipped doors in current view", doc):
        curview.IsolateElementsTemporary(flippedId)
else:
    Alert("GREAT JOB!\nKeep up the good work!", title=tits, header = str(counter) + " flipped doors were found.")