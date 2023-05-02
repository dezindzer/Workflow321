from pyrevit import forms
from pyrevit import revit, DB
from pyrevit.framework import List

doc = revit.doc

sheets = List[DB.ElementId]\
    ([i.Id for i in DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType() if len(i.GetAllViewports()) == 0])

message = 'There are {} empty Sheets in the current model. Are you sure you want to delete them?'.format(str(len(sheets)))

if len(sheets) == 0:
    forms.alert("No empty Sheets, well done!")
else:
    if forms.alert(message, ok=False, yes=True, no=True, exitscript=True):
        with revit.Transaction("Delete imported patterns"):
            try:
                s_names = [doc.GetElement(s).Title for s in sheets] # Get sheet names  
                doc.Delete(sheets)  # Delete the sheets 
                # print result
                print("SHEETS DELETED:\n")
                for s in s_names:
                    print("{}".format(s))
            except:
                forms.alert("Could not execute the script (make sure there are no active empty Sheets).")