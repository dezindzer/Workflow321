from Autodesk.Revit.UI import TaskDialog
from pyrevit.revit import doc, Transaction

if not doc.IsFamilyDocument:
    TaskDialog.Show('pyRevitPlus', 'Must be in Family Document.')

else:
    family_types = [x for x in doc.FamilyManager.Types]
    sorted_type_names = sorted([x.Name for x in family_types])
    current_type = doc.FamilyManager.CurrentType

    # Iterate through sorted list of type names, return name of next in list
    for n, type_name in enumerate(sorted_type_names):
        if type_name == current_type.Name:
            try:
                next_family_type_name = sorted_type_names[n + 1]
            except IndexError:
                # wraps list back to 0 if current is last
                next_family_type_name = sorted_type_names[0]

    for family_type in family_types:
        if family_type.Name == next_family_type_name:
            with Transaction("Cycle Type", doc):
                doc.FamilyManager.CurrentType = family_type