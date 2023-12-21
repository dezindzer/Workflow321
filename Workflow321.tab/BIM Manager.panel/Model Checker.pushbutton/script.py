# -*- coding: utf-8 -*-
import  os
from pyrevit import revit, DB, script, forms
from pyrevit.revit import doc
from pyrevit.revit.db import query
from Autodesk.Revit.DB import *

ft=304.8
mm=3.280839
output = script.get_output()
matching_elementsA = [] # list to store the elements that match the criteria
matching_elementsB = [] # list to store the elements that match the criteria
matching_elementsC = [] # list to store the elements that match the criteria

collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CurtainWallPanels) # filtered element collector

for element in collector: # Iterate through the elements and check if they have the specified parameter
    paramA = element.LookupParameter("Sirina A") # Get the parameter to search for
    if paramA is not None and paramA.HasValue: # Check if the parameter exists and has a value
        matching_elementsA.append(element)
    paramB = element.LookupParameter("Sirina B") # Get the parameter to search for
    if paramB is not None and paramB.HasValue: # Check if the parameter exists and has a value
        matching_elementsB.append(element)
    paramC = element.LookupParameter("Sirina C") # Get the parameter to search for
    if paramC is not None and paramC.HasValue: # Check if the parameter exists and has a value
        matching_elementsC.append(element)
        
counter=0
with revit.Transaction("test", doc):
    for element in matching_elementsA: 
        A = element.GetParameters("Width")[0].AsValueString() #Width
        B = element.GetParameters("Height")[0].AsValueString() #Height
        #print(A,B)
        #if A<B:
        SirinaA = element.GetParameters("Sirina A")[0].AsValueString()
        VisinaA = element.GetParameters("Visina A")[0].AsValueString()
        AX = element.GetParameters("Udaljenost ose A od vert. ivice")[0]
        AY = element.GetParameters("Visina ose A")[0]
        TestAXLeft = (27.0 + float(SirinaA)/2.0)/ft
        TestAXRight = (float(A) - 27.0 - float(SirinaA)/2.0)/ft
        TestAYTop = (float(B) - 27.0 - float(VisinaA)/2.0)/ft
        TestAYBottom = (27.0 + float(VisinaA)/2.0)/ft
        
        if TestAXLeft > AX.AsDouble():
            AX.Set(TestAXLeft)
            counter=counter+1
            print('AX Left ├ id: {}'.format(output.linkify(element.Id)))
        if AX.AsDouble() > TestAXRight:
            AX.Set(TestAXRight)
            counter=counter+1
            print('AX Right ├ id: {}'.format(output.linkify(element.Id)))
        if TestAYBottom > AY.AsDouble():
            AY.Set(TestAYBottom)
            counter=counter+1
            print('AX Bottom ├ id: {}'.format(output.linkify(element.Id)))
        if AY.AsDouble() > TestAYTop:
            AY.Set(TestAYTop)
            counter=counter+1
            print('AX Top ├ id: {}'.format(output.linkify(element.Id)))
                
        # else:
        #     SirinaA = element.GetParameters("Sirina A")[0].AsValueString()
        #     VisinaA = element.GetParameters("Visina A")[0].AsValueString()
        #     AX = element.GetParameters("Udaljenost ose A od vert. ivice")[0]
        #     AY = element.GetParameters("Visina ose A")[0]
        #     TestAXLeft = (27.0 + float(SirinaA)/2.0)/ft
        #     TestAXRight = (float(B) - 27.0 - float(SirinaA)/2.0)/ft
        #     TestAYTop = (float(A) - 27.0 - float(VisinaA)/2.0)/ft
        #     TestAYBottom = (27.0 + float(VisinaA)/2.0)/ft
            
        #     if TestAXLeft > AX.AsDouble():
        #         AX.Set(TestAXLeft)
        #         counter=counter+1
        #         print('AX Left ├ id: {}'.format(output.linkify(element.Id)))
        #     if AX.AsDouble() > TestAXRight:
        #         AX.Set(TestAXRight)
        #         counter=counter+1
        #         print('AX Right ├ id: {}'.format(output.linkify(element.Id)))
        #     if TestAYBottom > AY.AsDouble():
        #         AY.Set(TestAYBottom)
        #         counter=counter+1
        #         print('AX Bottom ├ id: {}'.format(output.linkify(element.Id)))
        #     if AY.AsDouble() > TestAYTop:
        #         AY.Set(TestAYTop)
        #         counter=counter+1
        #         print('AX Top ├ id: {}'.format(output.linkify(element.Id)))
                
    for element in matching_elementsB: 
            A = element.GetParameters("Width")[0].AsValueString() #Width
            B = element.GetParameters("Height")[0].AsValueString() #Height
            
            SirinaB = element.GetParameters("Sirina B")[0].AsValueString()
            VisinaB = element.GetParameters("Visina B")[0].AsValueString()
            BX = element.GetParameters("Udaljenost ose B od vert. ivice")[0]
            BY = element.GetParameters("Visina ose B")[0]
            TestBXLeft = (27.0 + float(SirinaB)/2.0)/ft
            TestBXRight = (float(A) - 27.0 - float(SirinaB)/2.0)/ft
            TestBYTop = (float(B) - 27.0 - float(VisinaB)/2.0)/ft
            TestBYBottom = (27.0 + float(VisinaB)/2.0)/ft
            
            if TestBXLeft > BX.AsDouble():
                BX.Set(TestBXLeft)
                counter=counter+1
                print('BX Left ├ id: {}'.format(output.linkify(element.Id)))
            if BX.AsDouble() > TestBXRight:
                BX.Set(TestBXRight)
                counter=counter+1
                print('BX Right ├ id: {}'.format(output.linkify(element.Id)))
            if TestBYBottom > BY.AsDouble():
                BY.Set(TestBYBottom)
                counter=counter+1
                print('BX Bottom ├ id: {}'.format(output.linkify(element.Id)))
            if BY.AsDouble() > TestBYTop:
                BY.Set(TestBYTop)
                counter=counter+1
                print('BX Top ├ id: {}'.format(output.linkify(element.Id)))

    for element in matching_elementsC: 
            A = element.GetParameters("Width")[0].AsValueString() #Width
            B = element.GetParameters("Height")[0].AsValueString() #Height
            
            SirinaC = element.GetParameters("Sirina C")[0].AsValueString()
            VisinaC = element.GetParameters("Visina C")[0].AsValueString()
            CX = element.GetParameters("Udaljenost ose C od vert. ivice")[0]
            CY = element.GetParameters("Visina ose C")[0]
            TestCXLeft = (27.0 + float(SirinaC)/2.0)/ft
            TestCXRight = (float(A) - 27.0 - float(SirinaC)/2.0)/ft
            TestCYTop = (float(B) - 27.0 - float(VisinaC)/2.0)/ft
            TestCYBottom = (27.0 + float(VisinaC)/2.0)/ft
            
            if TestCXLeft > CX.AsDouble():
                CX.Set(TestCXLeft)
                counter=counter+1
                print('CX Left ├ id: {}'.format(output.linkify(element.Id)))
            if CX.AsDouble() > TestCXRight:
                CX.Set(TestCXRight)
                counter=counter+1
                print('CX Right ├ id: {}'.format(output.linkify(element.Id)))
            if TestCYBottom > CY.AsDouble():
                CY.Set(TestCYBottom)
                counter=counter+1
                print('CX Bottom ├ id: {}'.format(output.linkify(element.Id)))
            if CY.AsDouble() > TestCYTop:
                CY.Set(TestCYTop)
                counter=counter+1
                print('CX Top ├ id: {}'.format(output.linkify(element.Id)))

print(counter)