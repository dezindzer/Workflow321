namespace CreateRoof
{
    {
        {

            CurveArray footprint = application.Create.NewCurveArray();
            
            ICollection<ElementId> selectedIds = uidoc.Selection.GetElementIds();
            if (selectedIds.Count != 0)
            {
                foreach (ElementId id in selectedIds)
                {
                    Element element = doc.GetElement(id);
                    Wall wall = element as Wall;
                    if (wall != null)
                    {
                        LocationCurve wallCurve = wall.Location as LocationCurve;
                        footprint.Append(wallCurve.Curve);
                        continue;
                    }

                    ModelCurve modelCurve = element as ModelCurve;
                    if (modelCurve != null)
                    {
                        footprint.Append(modelCurve.GeometryCurve);
                    }
                }
            }
            else
            {
                throw new Exception("You should select a curve loop, or a wall loop, or loops combination \nof walls and curves to create a footprint roof.");
            }

            ModelCurveArray footPrintToModelCurveMapping = new ModelCurveArray();
            FootPrintRoof footprintRoof = doc.Create.NewFootPrintRoof(footprint, level, roofType, out footPrintToModelCurveMapping);
            ModelCurveArrayIterator iterator = footPrintToModelCurveMapping.ForwardIterator();
            iterator.Reset();
            while (iterator.MoveNext())
            {
                ModelCurve modelCurve = iterator.Current as ModelCurve;
                footprintRoof.set_DefinesSlope(modelCurve, true);
                footprintRoof.set_SlopeAngle(modelCurve, 0.5);
            }

            return Result.Succeeded;
        }
    }
}