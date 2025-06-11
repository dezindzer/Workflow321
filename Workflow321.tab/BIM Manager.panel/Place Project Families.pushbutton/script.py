# This script for pyRevit/RevitPythonShell will place one instance of every loaded family
# into the active document in a grid on the first available level.

import clr
from System import Enum
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
#from pyrevit import revit, DB, script, forms
#from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    FamilySymbol,
    BuiltInCategory,
    Level,
    Transaction,
    XYZ,
)
from Autodesk.Revit.DB.Structure import StructuralType
from RevitServices.Persistence import DocumentManager

doc = DocumentManager.Instance.CurrentDBDocument

for bic in Enum.GetValues(BuiltInCategory):
    try:
        cat = doc.Settings.Categories.get_Item(bic)
        print(f"{bic}: {cat.Name}")
    except:
        print(f"{bic}: <no matching Category>")      
        
# collect all family symbols (types) in the project
#.OfClass(FamilySymbol)\
symbols = FilteredElementCollector(doc)\
    .OfCategory(BuiltInCategory.OST_Casework)\
    .WhereElementIsElementType()\
    .ToElements()

# pick a level to place on
levels = FilteredElementCollector(doc)\
    .OfClass(Level)\
    .ToElements()
if not levels:
    raise Exception("No levels found in project")
level = levels[0]

# grid parameters
spacing = 10.0  # feet (or project units)
cols = 10

t = Transaction(doc, "Place All Families")
t.Start()

x_idx = 0
y_idx = 0

for sym in symbols:
    # activate symbol if not already
    if not sym.IsActive:
        sym.Activate()
        doc.Regenerate()
    # compute insertion point
    pt = XYZ(x_idx * spacing, y_idx * spacing, 0)
    # place an instance
    doc.Create.NewFamilyInstance(pt, sym, level, StructuralType.NonStructural)
    # advance grid
    x_idx += 1
    if x_idx >= cols:
        x_idx = 0
        y_idx += 1

t.Commit()
