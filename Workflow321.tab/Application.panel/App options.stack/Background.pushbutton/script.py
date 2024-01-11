# This Python file uses the following encoding: utf-8
# IMPORTS
from Autodesk.Revit.DB import Color
from pyrevit import forms, HOST_APP
from pyrevit.forms import WarningBar
main_title="Select Background Color"
app = HOST_APP.app

# Code start
with WarningBar(title=main_title):
    color_select=forms.select_swatch(title=main_title)
    #print(color_select)
    if color_select != None:
        red = color_select.red
        green = color_select.green
        blue = color_select.blue
        
        SelectedColor = Color(red, green, blue)
        app.BackgroundColor = SelectedColor
        
        promptColorName = "Color name: " + color_select.name + "\n" 
        promptHEX = "HEX value: ( " + str(color_select) + " ) \n"
        promptRGB = "RGB value: ( " + str(red) + " , " + str(green) + " , "  + str(blue) + " )"
        
        forms.alert( promptColorName + promptHEX + promptRGB, ok=True, title="You selected the following color as the background:", exitscript=True)
    else:
        forms.alert('User canceled the operation', title="Canceled", warn_icon=True, exitscript=True)