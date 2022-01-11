with revit.Transaction("test", revit.doc):
    tkVrata = [ggg for ggg in doors if DB.Element.Name.GetValue(ggg).startswith('WD')]
    
def flipovana(vratay):
    flips = []
    for e in vratay:
            flip = 1 if e.HandFlipped else 0
            face = 1 if e.FacingFlipped else 0	
            flips.append(flip+face == 1)
    return(flips)


for e in tkVrata:
    mark = query.get_mark(e)
    name = query.get_name(e)
    revitID = get_revitid(e)
    test = query.get_episodeid(e)
    #print(mark, name, revitID, test)        

    #selection = ui.Selection(tkVrata)

vrataFlip = [sss for sss in doors if flipovana(tkVrata) & tkVrata]

print(vrataFlip)