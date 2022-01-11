from pyrevit import revit, DB
from pyrevit.revit.db import query
from pyrevit.framework import List, Guid
#from System import Guid

curtainWall= DB.FilteredElementCollector(revit.doc).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
curtainDoor = DB.FilteredElementCollector(revit.doc).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_Doors).ToElements()
lista = [curtainDoor, curtainWall]

guidSelekcijaOld = Guid('fd7fdc77-8cce-4acc-be92-c7a6e3c0bd02')
guidSelekcijaNew = Guid("8bd05530-a791-434c-9b5e-4a79207451dc")
guidSelekcijaHistory = Guid("9f8ffe79-6e87-4e6f-8a73-366812086618")

guids = [guidSelekcijaOld, guidSelekcijaNew, guidSelekcijaHistory]

with revit.Transaction("Clear Selkcija, Mark and Mark History", revit.doc):
    for l in lista:
        for w in l:
                mark = w.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).Set("")
                for g in guids:
                    override = w.get_Parameter(g)
                    try:
                        if override:
                            override.Set("")
                    except:
                        pass