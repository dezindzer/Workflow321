# This Python file uses the following encoding: utf-8

from pyrevit import revit, DB, script, forms, HOST_APP
from pyrevit.revit.db import query
from pyrevit.framework import List
from itertools import izip
from rpw import ui
from rpw.ui.forms import FlexForm, Label, TextBox, Button, ComboBox, Separator, CheckBox
from Autodesk.Revit import Exceptions, Creation
import math
import helper
import re

modelLine = DB.FilteredElementCollector(revit.doc).OfClass(DB.CurveElement).WhereElementIsNotElementType() # linija za offset kota koje se postavljaju automatski
kotes = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Entourage).WhereElementIsNotElementType().ToElements() # pronadji elemente koje koristimo za postavljanje koti

view = helper.get_view("Kotiranje Konstrukcije")[0] # view na kojem se kotira

refV = DB.ReferenceArray() # iniciranje ref array za vertikalne kote

refH = DB.ReferenceArray() # iniciranje ref array za horizontalne kote
outList = []


with revit.Transaction("Kotiranje", revit.doc):
    for m in modelLine:
        for e in kotes:
            VertikalnoKotiranje = e.LookupParameter("Vertikalno Kotiranje")
            HorizontalnoKotiranje = e.LookupParameter("Horizontalno Kotiranje")
            
            refV.Append(m.GeometryCurve.GetEndPointReference(0))
            #refV.Append(m.GeometryCurve.GetEndPointReference(1))
                
            if VertikalnoKotiranje.AsInteger() == 1:
                vKote = DB.FamilyInstance.GetReferenceByName(e,"Vertikalno")
                refV.Append(vKote)
                napraviKotuV = revit.doc.Create.NewDimension(view, m.GeometryCurve, refV)
                
            if HorizontalnoKotiranje.AsInteger() == 1:
                hKote = DB.FamilyInstance.GetReferenceByName(e,"Horizontalno")
                refH.Append(hKote)
                napraviKotuH = revit.doc.Create.NewDimension(view, m.GeometryCurve, refV)



##################################

    # for m,e in zip(modelLine,kotes):
    #     #try:
    #         VertikalnoKotiranje = e.LookupParameter("Vertikalno Kotiranje")
    #         HorizontalnoKotiranje = e.LookupParameter("Horizontalno Kotiranje")

    #         refV.Append(m.GeometryCurve.GetEndPointReference(0))
    #         refV.Append(m.GeometryCurve.GetEndPointReference(1))

    #         if VertikalnoKotiranje.AsInteger() == 1:
    #             vKote = DB.FamilyInstance.GetReferenceByName(e,"Vertikalno Kotiranje")
    #             refV.Append(vKote)
    #             napraviKotuV = revit.doc.Create.NewDimension(view, m.GeometryCurve, refV)

    #         else:
    #             pass

    #         if HorizontalnoKotiranje.AsInteger() == 1:
    #             hKote = DB.FamilyInstance.GetReferenceByName(e,"Horizontalno Kotiranje")
    #             refH.Append(hKote)
    #             napraviKotuH = revit.doc.Create.NewDimension(view, m.GeometryCurve, refV)
    #         else:
    #             pass
    #     # except Exception as e:
    #     #     outList.append(e.message)
