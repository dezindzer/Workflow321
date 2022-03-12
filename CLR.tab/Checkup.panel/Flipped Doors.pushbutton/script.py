# This Python file uses the following encoding: utf-8
from pyrevit import revit, DB, script, forms, HOST_APP
from pyrevit.revit.db import XYZPoint, query
from pyrevit.framework import List
from Autodesk.Revit import Exceptions
from rpw import ui
output = script.get_output()


tits = "Flipped Doors"
pogledi3D = DB.FilteredElementCollector(revit.doc).OfClass(DB.View3D)


viewTemplate = {v.Name: v for v in pogledi3D if v.IsTemplate}
first3Delement = pogledi3D.ToElements()
first3DView = first3Delement[0]

def get_revitid(element):
    return str(element.Id)[:30]

def get_view(some_name):
    view_name_filter = query.get_biparam_stringequals_filter({DB.BuiltInParameter.VIEW_NAME: some_name})
    found_view = DB.FilteredElementCollector(revit.doc) \
        .OfCategory(DB.BuiltInCategory.OST_Views) \
        .WherePasses(view_name_filter) \
        .WhereElementIsNotElementType().ToElements()
    return found_view

def apply_vt(v, vt):
    if vt:
        v.ViewTemplateId = vt.Id
    return

with revit.TransactionGroup(tits, revit.doc):
    #napravi VT ako ne postoji
    with revit.Transaction("Create View Template", revit.doc):
                if bool(viewTemplate) == False:
                    first3DView.Scale = 25
                    create3DTemplate = first3DView.CreateViewTemplate()
                    create3DTemplate.Name = tits
                    #viewTemplate[tits] = create3DTemplate
                    viewTemplateFlip = create3DTemplate
                else:   
                    viewTemplateFlip = viewTemplate[tits]
                    pass
    
    svaGledista = (DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewFamilyType))
    familyType  = [vt for vt in svaGledista.WhereElementIsElementType() if vt.FamilyName == "3D View"][0]
    doors = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType()

with revit.Transaction(tits, revit.doc):
    for door in doors:
        name = query.get_name(door) 
        mark = query.get_mark(door)
        revitID = DB.Element.Id.GetValue(door)
        if mark == "" or mark == None:
            mark = ""
        else:
            mark = " Mark " + mark + " - "
        #print(door) 
        prefix = 'WD'
        tkVrata = name.startswith(prefix) 
        if tkVrata == True:
            flips = []
            flip = 1 if door.HandFlipped else 0
            face = 1 if door.FacingFlipped else 0	
            flips.append(flip+face == 1)
            if flips[0] == True:
                sss=[]
                for view in enumerate(flips):
                    wallHost= door.Host
                    view = DB.View3D.CreateIsometric(revit.doc, familyType.Id)
                    apply_vt(view, viewTemplateFlip)
                    #try:
                    BoundingBoxXYZ = wallHost.get_BoundingBox(view)                
                    view.SetSectionBox(BoundingBoxXYZ)
                    viewName = name + " - " + mark + " ID " + str(revitID)
                    #loop za proveru da li ime vec postoji, ako da, napravi novi sa Copy 1 tagom
                    while get_view(viewName):
                        viewName = viewName + " Copy 1"
                    view.Name = viewName
                    
                    #print("{0} \t {1} {2}".format(output.linkify(view.Id), mark, name)) 

#msg = "Postoje flipovana vrata u projektu. Za njih su napravljeni 3D crteži."
#ui.forms.Alert(msg, title=tits)                    