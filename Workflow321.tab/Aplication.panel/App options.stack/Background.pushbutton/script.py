# This Python file uses the following encoding: utf-8
# IMPORTS
from Autodesk.Revit.DB import Color
from pyrevit import forms, HOST_APP
from pyrevit.forms import WarningBar

# VARIABLES
main_title="Select Background Color"
app = HOST_APP.app

# Code start
with WarningBar(title=main_title):
    color_select=forms.select_swatch(title=main_title)
    
    red = color_select.red
    green = color_select.green
    blue = color_select.blue
    colorName = color_select.name

SelectedColor = Color(red, green, blue)
app.BackgroundColor = SelectedColor


forms.alert("Color name: " + colorName + "\n" + "RGB value: (" + str(red) + " ," + str(green) + " ,"  + str(blue) + ")", ok=True, title="You selected the following color as the background:", exitscript=True)