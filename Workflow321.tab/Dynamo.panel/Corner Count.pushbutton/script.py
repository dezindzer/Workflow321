# -*- coding: utf-8 -*-
# pyRevit script: Count room corners
# Place this file as: %appdata%\pyRevit\Extensions\<yourext>.extension\<yourtab>.tab\<yourpanel>.panel\Count Room Corners.pushbutton\script.py

from __future__ import print_function
import sys
import math
from Autodesk.Revit import DB

import os, tempfile
from Autodesk.Revit.DB import BindingMap
app = __revit__.Application # type: ignore

# Revit / pyRevit imports
from Autodesk.Revit.DB import SpatialElementBoundaryLocation
from Autodesk.Revit.UI import TaskDialog
from math import cos, radians, sqrt, atan2, degrees

uidoc = __revit__.ActiveUIDocument  # type: ignore # noqa
doc = uidoc.Document
Z_EPS = 1e-9  # tiny threshold for cross/degenerate checks

# --- Tunables (feet / degrees)
XY_TOL = 0.01              # position tolerance
ANGLE_COL_DEG = 5.0        # straight if turn < 5°
RIGHT_TOL_DEG = 12.0       # 90° tolerance
COS_COL = cos(radians(ANGLE_COL_DEG))
TEETH_MAX_AREA = 6.0       # ft² cap for notch patch (keep modest)
NOTCH_DEPTH_MAX = 0.40     # ft (~5 in) max offset from main line to consider it a notch

def _get_or_create_room_int_param(doc, name):
    """
    Ensure an Integer instance parameter 'name' is bound to Rooms.
    Returns True if ready for writing, False otherwise.
    """
    # Does it already exist & is it integer?
    tmp_room = next(
        (r for r in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()),
        None
    )
    if tmp_room is not None:
        p = tmp_room.LookupParameter(name)
        if p:
            if p.StorageType == DB.StorageType.Integer:
                return True
            else:
                print("Parameter '{}' exists but is not Integer (found {}). Skipping writes for it."
                    .format(name, p.StorageType))
                return False

    # Create via shared parameter binding
    tg = DB.TransactionGroup(doc, "Bind room parameter '{}'".format(name))
    tg.Start()

    try:
        # 1) Make sure we have a shared parameter file
        spf_path = app.SharedParametersFilename
        cleanup_path = None
        if not spf_path or not os.path.isfile(spf_path):
            # create a temp shared parameter file
            fd, spf_path = tempfile.mkstemp(prefix="pyRevit_room_params_", suffix=".txt")
            os.close(fd)
            cleanup_path = spf_path
            app.SharedParametersFilename = spf_path

        spf = app.OpenSharedParameterFile()
        if spf is None:
            raise Exception("Could not open shared parameter file.")

        # 2) Create (or reuse) a group and the definition
        grp = next((g for g in spf.Groups if g.Name == "pyRevit Room Corners"), None)
        if grp is None:
            grp = spf.Groups.Create("pyRevit Room Corners")

        # Revit 2021- (old API) vs 2022+ (SpecTypeId)
        ext_def = None
        try:
            # New API
            from Autodesk.Revit.DB import ExternalDefinitionCreationOptions, SpecTypeId
            opts = ExternalDefinitionCreationOptions(name, SpecTypeId.Int)
            opts.Visible = True
            ext_def = grp.Definitions.Create(opts)
        except Exception:
            # Old API
            from Autodesk.Revit.DB import ExternalDefinitionCreationOptions, ParameterType
            opts = ExternalDefinitionCreationOptions(name, ParameterType.Integer)
            opts.Visible = True
            ext_def = grp.Definitions.Create(opts)

        # 3) Bind to Rooms as instance parameter under PG_DATA
        cats = app.Create.NewCategorySet()
        cats.Insert(doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Rooms))
        binding = app.Create.NewInstanceBinding(cats)

        t = DB.Transaction(doc, "Bind '{}' to Rooms".format(name))
        t.Start()
        try:
            pm = doc.ParameterBindings  # type: BindingMap
            success = pm.Insert(ext_def, binding, DB.BuiltInParameterGroup.PG_DATA)
            if not success:
                # Try re-insert (e.g., if exists but unbound)
                pm.ReInsert(ext_def, binding, DB.BuiltInParameterGroup.PG_DATA)
            t.Commit()
        except Exception as e:
            t.RollBack()
            raise

        tg.Assimilate()
        # clean temporary spf if we created it (don’t unset the app path)
        if cleanup_path and os.path.isfile(cleanup_path):
            # keep it; Revit needs it for the binding to remain resolvable during session
            pass

        return True
    except Exception as ex:
        tg.RollBack()
        print("Failed to bind parameter '{}': {}".format(name, ex))
        return False

def _ring_area_signed(pts):
    """Signed area (XY); >0 => CCW, <0 => CW."""
    n = len(pts)
    if n < 3: return 0.0
    a = 0.0
    for i in range(n):
        p1, p2 = pts[i], pts[(i+1) % n]
        a += p1.X * p2.Y - p2.X * p1.Y
    return 0.5 * a

def _classify_corners_out_in(pts):
    """Return (outward_count, inward_count)."""
    n = len(pts)
    if n < 3: return (0, 0)
    orient_sign = 1.0 if _ring_area_signed(pts) > 0.0 else -1.0

    outward = inward = 0
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]

        # vectors: incoming (p0->p1), outgoing (p1->p2)
        vin  = (p1.X - p0.X, p1.Y - p0.Y)
        vout = (p2.X - p1.X, p2.Y - p1.Y)

        # skip degenerate/straight vertices (should be rare after simplify)
        nvin  = (vin[0]*vin[0] + vin[1]*vin[1]) ** 0.5
        nvout = (vout[0]*vout[0] + vout[1]*vout[1]) ** 0.5
        if nvin < 1e-9 or nvout < 1e-9:
            continue
        # straight?
        if _cos_between(vin, vout) >= COS_COL:
            continue

        # signed turn via 2D cross (z-component)
        z = vin[0]*vout[1] - vin[1]*vout[0]

        if orient_sign * z > 0.0:
            outward += 1
        else:
            inward += 1
    return outward, inward

def count_room_corners_split(room, boundary_loc=SpatialElementBoundaryLocation.Finish):
    """Return (outward_count, inward_count, total_after_simplify)."""
    loops = _ordered_loops(room, boundary_loc)
    ring = _pick_outer_loop(loops)
    if len(ring) < 3: 
        return (0, 0, 0)
    ring = _simplify_notches(ring)
    ring = _collapse_colinear(ring)
    outc, inc = _classify_corners_out_in(ring)
    return outc, inc, outc + inc

def _eq_xy(p, q, tol=XY_TOL):
    return abs(p.X - q.X) <= tol and abs(p.Y - q.Y) <= tol

def _v2(a, b):  # vector a->b
    return (b.X - a.X, b.Y - a.Y)

def _dot(v1, v2): return v1[0]*v2[0] + v1[1]*v2[1]
def _crs(v1, v2): return v1[0]*v2[1] - v1[1]*v2[0]
def _nrm(v): return sqrt(v[0]*v[0] + v[1]*v[1])

def _cos_between(v1, v2):
    n1 = _nrm(v1); n2 = _nrm(v2)
    if n1 < 1e-9 or n2 < 1e-9: return 1.0
    return _dot(v1, v2) / (n1*n2)

def _turn_deg(v_in, v_out):
    if _nrm(v_in) < 1e-9 or _nrm(v_out) < 1e-9: return 0.0
    return degrees(atan2(_crs(v_in, v_out), _dot(v_in, v_out)))

def _quad_area_abs(p0, p1, p2, p3):
    x = [p0.X, p1.X, p2.X, p3.X]
    y = [p0.Y, p1.Y, p2.Y, p3.Y]
    a = x[0]*y[1] - x[1]*y[0] + x[1]*y[2] - x[2]*y[1] + x[2]*y[3] - x[3]*y[2] + x[3]*y[0] - x[0]*y[3]
    return abs(0.5*a)

def _ordered_loops(room, boundary_loc=SpatialElementBoundaryLocation.Finish):
    sbo = DB.SpatialElementBoundaryOptions()
    sbo.SpatialElementBoundaryLocation = boundary_loc
    loops = []
    for loop in room.GetBoundarySegments(sbo) or []:
        if not loop: continue
        pts = []
        for i, seg in enumerate(loop):
            crv = seg.GetCurve()
            if i == 0:
                pts.append(crv.GetEndPoint(0))
            pts.append(crv.GetEndPoint(1))
        # remove consecutive duplicates and closing duplicate
        clean = []
        for p in pts:
            if not clean or not _eq_xy(clean[-1], p):
                clean.append(p)
        if len(clean) >= 2 and _eq_xy(clean[0], clean[-1]):
            clean.pop()
        if len(clean) >= 3:
            loops.append(clean)
    return loops

def _ring_area_abs(pts):
    n = len(pts)
    if n < 3: return 0.0
    a = 0.0
    for i in range(n):
        p1, p2 = pts[i], pts[(i+1)%n]
        a += p1.X*p2.Y - p2.X*p1.Y
    return abs(0.5*a)

def _perp_offset_point_to_line(p, a, b):
    """Perpendicular distance from point p to infinite line through a->b."""
    v = _v2(a, b)
    w = _v2(a, p)
    nv = _nrm(v)
    if nv < 1e-9: 
        return 0.0
    return abs(_crs(w, v)) / nv

def _simplify_notches(pts):
    """Remove only shallow T-join notches (small depth off the main line)."""
    if len(pts) < 5:
        return pts
    pts = list(pts)
    changed = True
    while changed and len(pts) >= 5:
        changed = False
        n = len(pts)
        i = 0
        while i < n and n >= 5:
            p0 = pts[i % n]
            p1 = pts[(i+1) % n]
            p2 = pts[(i+2) % n]
            p3 = pts[(i+3) % n]

            v01 = _v2(p0, p1)      # main before detour
            v12 = _v2(p1, p2)      # first detour edge
            v23 = _v2(p2, p3)      # main after detour

            ang1 = _turn_deg(v01, v12)
            ang2 = _turn_deg(v12, v23)

            is_right_pair = (abs(abs(ang1) - 90.0) <= RIGHT_TOL_DEG and
                            abs(abs(ang2) - 90.0) <= RIGHT_TOL_DEG and
                            ang1 * ang2 < 0.0)  # opposite signs

            same_dir = _cos_between(v01, v23) >= COS_COL

            # NEW: notch must be shallow relative to main line p0->p3
            d1 = _perp_offset_point_to_line(p1, p0, p3)
            d2 = _perp_offset_point_to_line(p2, p0, p3)
            shallow = (d1 <= NOTCH_DEPTH_MAX and d2 <= NOTCH_DEPTH_MAX)

            small_area = _quad_area_abs(p0, p1, p2, p3) <= TEETH_MAX_AREA

            if is_right_pair and same_dir and shallow and small_area:
                # remove the two notch vertices
                del pts[(i+1) % n]
                n = len(pts)
                del pts[(i+1) % n]
                n = len(pts)
                changed = True
                i = max(i-2, 0)
                continue

            i += 1
    return pts

def _collapse_colinear(pts):
    """Remove vertices where the path continues straight (within ANGLE_COL_DEG)."""
    n = len(pts)
    if n < 3: return pts
    keep = []
    for i in range(n):
        p0 = pts[(i-1) % n]
        p1 = pts[i]
        p2 = pts[(i+1) % n]
        if _eq_xy(p0, p1) or _eq_xy(p1, p2):  # dupes
            continue
        vin = _v2(p0, p1)
        vout = _v2(p1, p2)
        # straight if turn is small and in same direction
        if _cos_between(vin, vout) >= COS_COL:
            continue
        keep.append(p1)
    return keep

def _pick_outer_loop(loops):
    return max(loops, key=_ring_area_abs) if loops else []

def count_room_corners(room, boundary_loc=SpatialElementBoundaryLocation.Finish):
    loops = _ordered_loops(room, boundary_loc)
    ring = _pick_outer_loop(loops)
    if len(ring) < 3: return 0
    ring = _simplify_notches(ring)
    ring = _collapse_colinear(ring)
    return len(ring)


def eid_str(eid):
    """Robust ElementId -> string for logging."""
    try:
        return str(eid.IntegerValue)          # typical
    except Exception:
        try:
            return str(int(str(eid)))         # fallback via ToString()
        except Exception:
            return "<unknown-id>"

def xy_key(pt):
    """Hash an XYZ to a 2D grid key with XY tolerance."""
    return (int(round(pt.X / XY_TOL)), int(round(pt.Y / XY_TOL)))

def get_room_boundary_vertices(room):
    """Return a set of unique XY vertices for the room boundary."""
    sbo = DB.SpatialElementBoundaryOptions()
    # Choose the boundary location you prefer:
    # sbo.DB.SpatialElementBoundaryLocation = DB.SpatialElementBoundaryLocation.Finish
    sbo.DB.SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.CoreBoundary

    loops = room.GetBoundarySegments(sbo)
    if not loops:
        return set()

    verts_xy = set()
    for loop in loops:
        if not loop:
            continue
        for seg in loop:
            crv = seg.GetCurve()
            sp = crv.GetEndPoint(0)
            ep = crv.GetEndPoint(1)
            verts_xy.add(xy_key(sp))
            verts_xy.add(xy_key(ep))
    return verts_xy

def rooms_from_selection():
    """Return Room elements from current selection; empty if none."""
    sel_ids = list(uidoc.Selection.GetElementIds())
    rooms = []
    if sel_ids:
        for eid in sel_ids:
            el = doc.GetElement(eid)
            if not el or not el.Category:
                continue
            # Safer category check
            if el.Category.Id == DB.ElementId(DB.BuiltInCategory.OST_Rooms):
                if el.Area > 0:
                    rooms.append(el)
    return rooms

def all_rooms():
    """Return all placed Rooms."""
    return [
        r for r in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()
        if r.Area > 0
    ]

def main():
    target_rooms = rooms_from_selection()
    mode = "selection" if target_rooms else "all rooms"
    if not target_rooms:
        target_rooms = all_rooms()

    if not target_rooms:
        print("No placed Rooms found.")
        return

    #print("Room corner count ({}):\n".format(mode))
    total = 0
    failures = 0

    for room in target_rooms:
        try:
            #count = count_room_corners(room)
            #count = count_room_corners(room, SpatialElementBoundaryLocation.Finish)
            outc, inc, total = count_room_corners_split(room, SpatialElementBoundaryLocation.Finish)
            #total += count
            
            rmnum = room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString() if room.LookupParameter("Number") else room.Number
            rmname = room.LookupParameter("Name").AsString() if room.LookupParameter("Name") else "<unnamed>"
            print('- Room {} "{}": {} corners ({} outward, {} inward)'.format(rmnum, rmname, total, outc, inc))
            # Ensure parameters exist once (before the loop)
            ok_out = _get_or_create_room_int_param(doc, "outward")
            ok_in  = _get_or_create_room_int_param(doc, "inward")
            # Wrap writes in a single transaction
            twrite = DB.Transaction(doc, "Write room corner counts")
            twrite.Start()
            for room in target_rooms:
                try:
                    outc, inc, total = count_room_corners_split(room, SpatialElementBoundaryLocation.Finish)
                    
                    # Write values if params are available & integer
                    if ok_out:
                        p_out = room.LookupParameter("outward")
                        if p_out and p_out.StorageType == DB.StorageType.Integer:
                            p_out.Set(int(outc))
                    if ok_in:
                        p_in = room.LookupParameter("inward")
                        if p_in and p_in.StorageType == DB.StorageType.Integer:
                            p_in.Set(int(inc))
                    
                    # print('- Room {} "{}": {} corners ({} outward, {} inward)'
                    #     .format(rmnum, rmname, total, outc, inc))
                    
                except Exception as ex:
                    failures += 1
                    print("- Room <id {}>: ERROR ({})".format(eid_str(room.Id), ex))
                    
            twrite.Commit()
            
        except Exception as ex:
            failures += 1
            print("- Room <id {}>: ERROR ({})".format(eid_str(room.Id), ex))
    
    #print("\nProcessed {} room(s). Total corners (sum of per-room counts): {}.".format(len(target_rooms), total))
    if failures:
        print("Completed with {} error(s).".format(failures))

if __name__ == "__main__":
    main()
