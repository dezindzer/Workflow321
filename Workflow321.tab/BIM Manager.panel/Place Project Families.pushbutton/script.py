# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import (
    FilteredElementCollector, 
    FamilySymbol, 
    Level, 
    XYZ, 
    CategoryType,
    Transaction
)
from Autodesk.Revit.DB.Structure import StructuralType
from pyrevit import revit, forms, script
import math

doc = revit.doc

def is_model_category(category):
    if category and category.CategoryType == CategoryType.Model:
        exclude = ["Mass", "Shaft Opening", "Stairs Landing", "Stairs Run"]
        return category.Name not in exclude
    return False

def run():
    # 1. Prikupljanje svih simbola za meni
    all_symbols = FilteredElementCollector(doc).OfClass(FamilySymbol).ToElements()
    cat_dict = {}
    
    # 2. Pronalaženje tvoje specijalne familije za naslov
    # Tražimo simbol familije koja se zove "Model Text"
    title_family_symbol = None
    for s in all_symbols:
        if s.Family.Name == "Model Text":
            title_family_symbol = s
            break
            
        # Grupisanje ostalih modela
        if s.Category and is_model_category(s.Category):
            cat_name = s.Category.Name
            cat_dict.setdefault(cat_name, []).append(s)

    if not title_family_symbol:
        forms.alert("Greška: Familija 'Model Text' nije pronađena u projektu.\nUčitaj familiju pa pokreni ponovo.")
        return

    # 3. UI Selekcija
    selected_categories = forms.SelectFromList.show(
        sorted(cat_dict.keys()),
        title='Odaberi kategorije',
        multiselect=True
    )
    if not selected_categories:
        return

    level = FilteredElementCollector(doc).OfClass(Level).FirstElement()
    
    # Parametri rasporeda
    spacing = 20.0 
    category_spacing = 60.0 
    cols = 6
    current_y_offset = 0

    with revit.Transaction("Generisanje biblioteke sa 3D naslovima"):
        # Aktiviraj simbol za naslov ako nije aktivan
        if not title_family_symbol.IsActive:
            title_family_symbol.Activate()

        for cat_name in selected_categories:
            symbols = cat_dict[cat_name]
            
            # --- POSTAVLJANJE NASLOVA (Tvoja familija) ---
            text_pos = XYZ(0, current_y_offset + 15, 0)
            try:
                # Postavljamo instancu tvoje familije
                title_instance = doc.Create.NewFamilyInstance(
                    text_pos, 
                    title_family_symbol, 
                    level, 
                    StructuralType.NonStructural
                )
                
                # Menjamo Instance parametar "Model Text"
                # (Pretpostavljam da se parametar zove tačno tako, proveri mala/velika slova)
                param = title_instance.LookupParameter("Model Text")
                if param:
                    param.Set(cat_name.upper())
                else:
                    print("Upozorenje: Parametar 'Model Text' nije pronađen na instanci.")
            except Exception as e:
                print("Greška pri postavljanju naslova: {}".format(e))

            # --- GRID ZA FAMILIJE ---
            x_idx = 0
            y_idx = 0
            for sym in symbols:
                # Preskačemo samu familiju "Model Text" da je ne bismo ređali u gridu
                if sym.Family.Name == "Model Text":
                    continue

                if not sym.IsActive:
                    sym.Activate()
                
                pt = XYZ(x_idx * spacing, current_y_offset - (y_idx * spacing), 0)
                try:
                    doc.Create.NewFamilyInstance(pt, sym, level, StructuralType.NonStructural)
                except:
                    pass
                
                x_idx += 1
                if x_idx >= cols:
                    x_idx = 0
                    y_idx += 1
            
            # Pomeranje offseta za sledeću kategoriju
            num_rows = math.ceil(len(symbols) / float(cols)) if symbols else 1
            current_y_offset -= (num_rows * spacing + category_spacing)

    print("Uspešno kreirano sa 3D naslovima!")

if __name__ == "__main__":
    run()