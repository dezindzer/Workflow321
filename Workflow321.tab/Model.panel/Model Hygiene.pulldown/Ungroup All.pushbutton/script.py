from pyrevit import revit, DB, script, forms

# Gather groups
coll_groups = DB.FilteredElementCollector(revit.doc).OfClass(DB.Group).WhereElementIsNotElementType().ToElements()

ungr_ids=[]
if len(coll_groups) == 0:
    forms.alert("We're gonna get those bastards next time!", title="No groups found", footer="Don't lose hope!")
else:
    # warning
    if forms.alert(msg="Are you sure?",\
                sub_msg="Proceeding will ungroup all groups in the model.",\
                ok=True, cancel=True,\
                warn_icon=True):
        output = script.get_output()
        with revit.Transaction ("Ungroup All", revit.doc):
            try:
                forms.alert("Ungrouped {} groups".format(len(coll_groups)))
                for gr in coll_groups:
                    # Iterate through groups and ungroup
                    ungrouped = (gr.UngroupMembers())
            except:
                forms.alert("Error")