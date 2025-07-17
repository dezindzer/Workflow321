# Import necessary modules
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
clr.AddReference('RevitServices')

importlocation = "C:\Users\nikola.markovic\Desktop\Import"

exportlocation = "C:\Users\nikola.markovic\Desktop\Export"
extension = ".rfa"

def DirectoryContentsAll(directory, searchstring):
    from System.IO import Directory, SearchOption
    if Directory.Exists(directory):
        return Directory.GetFiles(directory, searchstring, SearchOption.AllDirectories)
    else:
        return list()



# Revit and Dynamo modules
from Autodesk.Revit.DB import Document, FamilySource, IFamilyLoadOptions
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

#input assigned to IN variable
importLocation = DirectoryContentsAll(importlocation, extension)
exportLocation = DirectoryContentsAll(exportlocation, extension)

#wrap input inside a list if not a list.
if not isinstance(importLocation, list): 
    importLocation = [importLocation]
if not isinstance(exportLocation, list): 
    exportLocation = [exportLocation]

#ensure loaded families can overwrite existing families.
class FamilyOption(IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues = True
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        source = FamilySource.Family
        overwriteParameterValues = True
        return True     

#core data processing
documents = []
families = []
for docpath in exportLocation:
    doc=app.OpenDocumentFile(docpath)
    documents.append(doc)
for path in importLocation:
    family_doc = app.OpenDocumentFile(path)
    families.append(family_doc)

for document in documents:
    map(lambda family: family.LoadFamily(document, FamilyOption()),
    families)

map(lambda x: x.Close(False), families)
map(lambda x: x.Close(True), documents)

# output assigned to the OUT variable
OUT = [importLocation, exportLocation]

#core data processing
for path in importLocation:
    try:
        famDoc = app.OpenDocumentFile(path)
        famDoc.LoadFamily(doc, FamilyOption())
        famDoc.Close(False)
    except:
        pass

#output assigned the OUT variable
OUT = importLocation