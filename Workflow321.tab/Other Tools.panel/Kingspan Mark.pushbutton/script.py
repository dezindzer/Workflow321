# This Python file uses the following encoding: utf-8

from pyrevit import DB, HOST_APP
from pyrevit.revit import doc, Transaction

curtainWall= DB.FilteredElementCollector(doc).WhereElementIsNotElementType().OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).ToElements()

KingspanPanels = [KP for KP in curtainWall if "Kingspan" in KP.Name]


with Transaction("Kingspan Mark", doc):
    for KingspanPanel in KingspanPanels:
        #mark = KingspanPanel.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK)
        #print(mark.AsValueString())
        paramHeight = float(KingspanPanel.LookupParameter("Height").AsValueString())
        #print(paramHeight)
        #print(float(paramHeight))
        
        k0 = 0.0
        k5k = 5000.0
        k8k = 8000.0
        k9k = 9000.0
        k12k = 12000.0
        
        if k0 < paramHeight < k5k+1.0:
            mark = KingspanPanel.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).Set("између 0 и 5м")
        elif k5k < paramHeight < k8k+1.0:
            mark = KingspanPanel.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).Set("између 5 и 8м")
        elif k8k < paramHeight < k9k+1.0:
            mark = KingspanPanel.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).Set("између 8 и 9м")
        elif k9k < paramHeight < k12k+1.0:
            mark = KingspanPanel.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).Set("између 9 и 12м")
        elif paramHeight > k12k:
            mark = KingspanPanel.get_Parameter(DB.BuiltInParameter.ALL_MODEL_MARK).Set("преко 12м")