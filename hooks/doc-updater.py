# # This Python file uses the following encoding: utf-8
# from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, ElementId, UnitUtils, UnitTypeId
# from pyrevit.revit import doc


# sender = __eventsender__ # type: ignore

# args = __eventargs__ # type: ignore

# modified_el_ids = args.GetModifiedElementIds()
# deleted_el_ids = args.GetDeletedElementIds()
# new_el_ids = args.GetAddedElementIds()

# modified_el = [doc.GetElement(e_id) for e_id in modified_el_ids]


# allowed_cats = [ElementId(BuiltInCategory.OST_Windows), ElementId(BuiltInCategory.OST_Doors),ElementId(BuiltInCategory.OST_CurtainWallPanels)]
# for el in modified_el:
#     if el.Category.Id in allowed_cats:
#         #print(el)
#         p_com = el.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
#         pt = el.Location.Point
#         x = round(UnitUtils.ConvertFromInternalUnits(pt.X, UnitTypeId.Meters), 2)
#         y = round(UnitUtils.ConvertFromInternalUnits(pt.Y, UnitTypeId.Meters), 2)
#         z = round(UnitUtils.ConvertFromInternalUnits(pt.Z, UnitTypeId.Meters), 2)
        
#         coord = "{},{},{}".format(x,y,z)
        
#         p_com.Set(coord)