from pyrevit import DB
from pyrevit.framework import Guid
from pyrevit.forms import alert
from pyrevit.revit import HOST_APP, Transaction, doc

# variables
host = HOST_APP.username

# get elements for clearing
curtainWall= DB.FilteredElementCollector(doc).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()
curtainDoor = DB.FilteredElementCollector(doc).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_Doors).ToElements()
lista = [curtainDoor, curtainWall]

# predefined shared parameters
guidSelekcijaOld = Guid('fd7fdc77-8cce-4acc-be92-c7a6e3c0bd02')
guidSelekcijaNew = Guid("8bd05530-a791-434c-9b5e-4a79207451dc")
guidSelekcijaHistory = Guid("9f8ffe79-6e87-4e6f-8a73-366812086618")
guids = [guidSelekcijaOld, guidSelekcijaNew, guidSelekcijaHistory]

#Code
if host == "bob" or host == "dezindzer":
    with Transaction("Clear Selkcija, Mark and Mark History", doc):
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
    alert(msg="Mark cleared!")
else:
    alert(title="Restricted!", 
                msg="Option not allowed for "+str(host), 
                sub_msg="Contact your BIM manager for access", 
                expanded="This option can break your current Marks. \nAfter Marking, the marks probably won't be the same as they were for each panel! ", 
                warn_icon=True)


