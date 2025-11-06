# -*- coding: utf-8 -*-
# Select one or multiple elements and recursively select all their subelements, excluding those in the "SITE" category.
import clr
from pyrevit import revit, DB, script
from pyrevit.revit import selection

clr.AddReference("System")
from System.Collections.Generic import List  # type: ignore

uidoc = revit.uidoc
doc = revit.doc
output = script.get_output()

# get current selection or prompt
sel = selection.get_selection()
if not sel:
    sel = [selection.pick_element("Select element(s)")]  # single if none preselected

if not sel:
    script.exit()

def get_subelements(element, depth=0):
    found = []
    for sid in element.GetSubComponentIds():
        subel = doc.GetElement(sid)
        if subel is None:
            continue

        cat = subel.Category
        is_excluded = (
            cat is not None
            and cat.Name is not None
            and (cat.Name.upper() == "SITE" or cat.Name.upper() == "ENTOURAGE")
        )

        if not is_excluded:
            found.append(subel.Id)

        deeper = get_subelements(subel, depth + 1)
        found.extend(deeper)

    return found


# collect all IDs from all selected elements
all_ids = []
for el in sel:
    subelement_ids = get_subelements(el)
    all_ids.append(el.Id)
    all_ids.extend(subelement_ids)

if all_ids:
    uidoc.Selection.SetElementIds(List[DB.ElementId](all_ids))
else:
    output.print_md("**No subelements found (excluding SITE).**")
