# -*- coding: utf-8 -*-
# main code by Erik Frits https://github.com/ErikFrits/
# updated to use pyRevit lib

from Autodesk.Revit.DB import WorksharingUtils, ElementId, FilteredElementCollector
from pyrevit import revit
from pyrevit.forms import SelectFromList
from System.Collections.Generic import List

uidoc     = revit.uidoc
doc       = revit.doc

elements = FilteredElementCollector(doc).WhereElementIsNotElementType().WhereElementIsViewIndependent().ToElements()

# Sort Elements by User LastChangedBy
from collections import defaultdict
elements_sorted_by_last_user = defaultdict(list)
for el in elements:
    try:
        wti = WorksharingUtils.GetWorksharingTooltipInfo(doc, el.Id)
        last = wti.LastChangedBy
        elements_sorted_by_last_user[last].append(el.Id)
    except:
        pass

# Select User
selected_user = SelectFromList.show(elements_sorted_by_last_user.keys(), button_name='Select User')

# Prepare Selected Elements
element_ids        = elements_sorted_by_last_user[selected_user]
List_new_selection = List[ElementId](element_ids)

# Change Revit UI Selection
uidoc.Selection.SetElementIds(List_new_selection)



