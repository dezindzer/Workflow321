# -*- coding: utf-8 -*-
# Select an element and recursively select all its subelements, excluding those in the "SITE" category.
import clr
from pyrevit import revit, DB, script
from pyrevit.revit import selection

clr.AddReference("System")
from System.Collections.Generic import List # type: ignore

uidoc = revit.uidoc
doc = revit.doc
output = script.get_output()

# pick one element
sel = selection.get_selection()
if not sel:
    el = selection.pick_element("Select an element")
else:
    el = sel[0]

if not el:
    script.exit()

def get_subelements(element, depth=0):
    """Recursively collect all subelements, skipping SITE category from selection but still checking its children."""
    found = []
    for sid in element.GetSubComponentIds():
        subel = doc.GetElement(sid)
        if subel is None:
            continue
        
        # excluded category
        cat = subel.Category
        # is_excluded = cat is not None and cat.Name is not None and cat.Name.upper() == "SITE" or cat.Name.upper() == "ENTOURAGE"
        is_excluded = (
            cat is not None
            and cat.Name is not None
            and (cat.Name.upper() == "SITE" or cat.Name.upper() == "ENTOURAGE")
        )

        # only add if not excluded category
        if not is_excluded:
            found.append(subel.Id)
           #output.print_md("  " * depth + "+ Added: {} ({})".format(subel.Id, cat.Name if cat else "No Category"))

        # recurse into subelements regardless of SITE
        deeper = get_subelements(subel, depth + 1)
        for d in deeper:
            found.append(d)

    return found

subelement_ids = get_subelements(el)

# include the originally selected element
all_ids = List[DB.ElementId]([el.Id] + subelement_ids)

if all_ids:
    uidoc.Selection.SetElementIds(all_ids)
    #output.print_md("**Selected {} subelements + main element.**".format(len(subelement_ids)))
else:
    output.print_md("**No subelements found (excluding SITE).**")
