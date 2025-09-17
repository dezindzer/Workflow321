# -*- coding: utf-8 -*-
# pyRevit script: Count room corners (outward / inward) and write to parameters

from __future__ import print_function
import os, tempfile
from math import cos, radians, sqrt, atan2, degrees
from Autodesk.Revit import DB
from Autodesk.Revit.DB import (
    FilteredElementCollector, BuiltInCategory, BuiltInParameter,
    SpatialElementBoundaryLocation, SpatialElementBoundaryOptions,
    Transaction, TransactionGroup, StorageType
)

uidoc = __revit__.ActiveUIDocument  # type: ignore
doc = uidoc.Document
app = __revit__.Application  # type: ignore

# ---------------- Tunables (feet / degrees) ----------------
XY_TOL = 0.01
ANGLE_COL_DEG = 5.0
RIGHT_TOL_DEG = 12.0
COS_COL = cos(radians(ANGLE_COL_DEG))
TEETH_MAX_AREA = 6.0      # ft²
NOTCH_DEPTH_MAX = 0.40    # ft

PARAM_OUT = "outward"
PARAM_IN  = "inward"

# ---------------- Geometry helpers (your existing ones) ----------------
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

def _ring_area_signed(pts):
    n = len(pts)
    if n < 3: return 0.0
    a = 0.0
    for i in range(n):
        p1, p2 = pts[i], pts[(i+1) % n]
        a += p1.X * p2.Y - p2.X * p1.Y
    return 0.5 * a

def _ring_area_abs(pts):
    n = len(pts)
    if n < 3: return 0.0
    a = 0.0
    for i in range(n):
        p1, p2 = pts[i], pts[(i+1)%n]
        a += p1.X*p2.Y - p2.X*p1.Y
    return abs(0.5*a)

def _quad_area_abs(p0, p1, p2, p3):
    x = [p0.X, p1.X, p2.X, p3.X]
    y = [p0.Y, p1.Y, p2.Y, p3.Y]
    a = x[0]*y[1] - x[1]*y[0] + x[1]*y[2] - x[2]*y[1] + x[2]*y[3] - x[3]*y[2] + x[3]*y[0] - x[0]*y[3]
    return abs(0.5*a)

def _perp_offset_point_to_line(p, a, b):
    v = _v2(a, b)
    w = _v2(a, p)
    nv = _nrm(v)
    if nv < 1e-9: 
        return 0.0
    return abs(_crs(w, v)) / nv

def _ordered_loops(room, boundary_loc=SpatialElementBoundaryLocation.Finish):
    sbo = SpatialElementBoundaryOptions()
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
        clean = []
        for p in pts:
            if not clean or not _eq_xy(clean[-1], p):
                clean.append(p)
        if len(clean) >= 2 and _eq_xy(clean[0], clean[-1]):
            clean.pop()
        if len(clean) >= 3:
            loops.append(clean)
    return loops

def _simplify_notches(pts):
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

            v01 = _v2(p0, p1)
            v12 = _v2(p1, p2)
            v23 = _v2(p2, p3)

            ang1 = _turn_deg(v01, v12)
            ang2 = _turn_deg(v12, v23)

            is_right_pair = (abs(abs(ang1) - 90.0) <= RIGHT_TOL_DEG and
                             abs(abs(ang2) - 90.0) <= RIGHT_TOL_DEG and
                             ang1 * ang2 < 0.0)

            same_dir = _cos_between(v01, v23) >= COS_COL

            d1 = _perp_offset_point_to_line(p1, p0, p3)
            d2 = _perp_offset_point_to_line(p2, p0, p3)
            shallow = (d1 <= NOTCH_DEPTH_MAX and d2 <= NOTCH_DEPTH_MAX)

            small_area = _quad_area_abs(p0, p1, p2, p3) <= TEETH_MAX_AREA

            if is_right_pair and same_dir and shallow and small_area:
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
    n = len(pts)
    if n < 3: return pts
    keep = []
    for i in range(n):
        p0 = pts[(i-1) % n]
        p1 = pts[i]
        p2 = pts[(i+1) % n]
        if _eq_xy(p0, p1) or _eq_xy(p1, p2):
            continue
        vin = _v2(p0, p1)
        vout = _v2(p1, p2)
        if _cos_between(vin, vout) >= COS_COL:
            continue
        keep.append(p1)
    return keep

def _pick_outer_loop(loops):
    return max(loops, key=_ring_area_abs) if loops else []

def _classify_corners_out_in(pts):
    n = len(pts)
    if n < 3: return (0, 0)
    orient_sign = 1.0 if _ring_area_signed(pts) > 0.0 else -1.0
    outward = inward = 0
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        vin  = (p1.X - p0.X, p1.Y - p0.Y)
        vout = (p2.X - p1.X, p2.Y - p1.Y)
        nvin  = (vin[0]*vin[0] + vin[1]*vin[1]) ** 0.5
        nvout = (vout[0]*vout[0] + vout[1]*vout[1]) ** 0.5
        if nvin < 1e-9 or nvout < 1e-9:
            continue
        if _cos_between(vin, vout) >= COS_COL:
            continue
        z = vin[0]*vout[1] - vin[1]*vout[0]
        if orient_sign * z > 0.0:
            outward += 1
        else:
            inward += 1
    return outward, inward

def count_room_corners_split(room, boundary_loc=SpatialElementBoundaryLocation.Finish):
    loops = _ordered_loops(room, boundary_loc)
    ring = _pick_outer_loop(loops)
    if len(ring) < 3: 
        return (0, 0, 0)
    ring = _simplify_notches(ring)
    ring = _collapse_colinear(ring)
    outc, inc = _classify_corners_out_in(ring)
    return outc, inc, outc + inc

def count_room_corners_split_with_holes(room, boundary_loc=SpatialElementBoundaryLocation.Finish):
    """Return (outward_count, inward_count, total_after_simplify) accounting for inner holes."""
    # 1) collect all loops
    loops = _ordered_loops(room, boundary_loc)
    if not loops:
        return (0, 0, 0)

    # 2) simplify each loop
    simp = []
    for L in loops:
        R = _simplify_notches(L)
        R = _collapse_colinear(R)
        if len(R) >= 3:
            simp.append(R)
    if not simp:
        return (0, 0, 0)

    # 3) find outer loop (largest |area|)
    areas_signed = [_ring_area_signed(L) for L in simp]
    areas_abs = [abs(a) for a in areas_signed]
    outer_idx = max(range(len(simp)), key=lambda i: areas_abs[i])
    outer_sign = 1.0 if areas_signed[outer_idx] > 0.0 else -1.0

    # 4) accumulate, swapping for holes (orientation opposite outer)
    out_total = 0
    in_total  = 0
    for L, a_signed in zip(simp, areas_signed):
        out_i, in_i = _classify_corners_out_in(L)  # uses L's own orientation
        this_sign = 1.0 if a_signed > 0.0 else -1.0
        if this_sign == outer_sign:
            # outer-like loop
            out_total += out_i
            in_total  += in_i
        else:
            # hole: swap meaning for the room
            out_total += in_i
            in_total  += out_i
    return out_total, in_total, out_total + in_total

# ---------------- Parameter binding helper ----------------
def _get_or_create_room_int_param(doc, name):
    # Check existing
    tmp_room = next((r for r in FilteredElementCollector(doc)
                    .OfCategory(BuiltInCategory.OST_Rooms)
                    .WhereElementIsNotElementType()), None)
    if tmp_room is not None:
        p = tmp_room.LookupParameter(name)
        if p:
            if p.StorageType == StorageType.Integer:
                return True
            else:
                print("Parameter '{}' exists but isn't Integer. Skipping writes.".format(name))
                return False

    tg = TransactionGroup(doc, "Bind room parameter '{}'".format(name))
    tg.Start()
    try:
        spf_path = app.SharedParametersFilename
        if not spf_path or not os.path.isfile(spf_path):
            fd, spf_path = tempfile.mkstemp(prefix="pyRevit_room_params_", suffix=".txt")
            os.close(fd)
            app.SharedParametersFilename = spf_path
        spf = app.OpenSharedParameterFile()
        if spf is None:
            raise Exception("Could not open shared parameter file.")

        grp = next((g for g in spf.Groups if g.Name == "pyRevit Room Corners"), None)
        if grp is None:
            grp = spf.Groups.Create("pyRevit Room Corners")

        try:
            from Autodesk.Revit.DB import ExternalDefinitionCreationOptions, SpecTypeId
            opts = ExternalDefinitionCreationOptions(name, SpecTypeId.Int)
            opts.Visible = True
            ext_def = grp.Definitions.Create(opts)
        except Exception:
            from Autodesk.Revit.DB import ExternalDefinitionCreationOptions, ParameterType
            opts = ExternalDefinitionCreationOptions(name, ParameterType.Integer)
            opts.Visible = True
            ext_def = grp.Definitions.Create(opts)

        cats = app.Create.NewCategorySet()
        cats.Insert(doc.Settings.Categories.get_Item(BuiltInCategory.OST_Rooms))
        binding = app.Create.NewInstanceBinding(cats)

        t = Transaction(doc, "Bind '{}' to Rooms".format(name))
        t.Start()
        try:
            pm = doc.ParameterBindings
            ok = pm.Insert(ext_def, binding, DB.BuiltInParameterGroup.PG_DATA)
            if not ok:
                pm.ReInsert(ext_def, binding, DB.BuiltInParameterGroup.PG_DATA)
            t.Commit()
        except:
            t.RollBack()
            raise

        tg.Assimilate()
        return True
    except Exception as ex:
        tg.RollBack()
        print("Failed to bind parameter '{}': {}".format(name, ex))
        return False

# ---------------- Selection helpers ----------------
def rooms_from_selection():
    sel_ids = list(uidoc.Selection.GetElementIds())
    rooms = []
    if sel_ids:
        for eid in sel_ids:
            el = doc.GetElement(eid)
            if not el or not el.Category:
                continue
            if el.Category.Id == DB.ElementId(BuiltInCategory.OST_Rooms):
                if getattr(el, "Area", 0.0) > 0.0:
                    rooms.append(el)
    return rooms

def all_rooms():
    return [r for r in FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_Rooms).ToElements()
            if getattr(r, "Area", 0.0) > 0.0]

# ---------------- Main ----------------
def main():
    target_rooms = rooms_from_selection()
    if not target_rooms:
        target_rooms = all_rooms()
    if not target_rooms:
        print("No placed Rooms found.")
        return

    # Ensure params exist once
    ok_out = _get_or_create_room_int_param(doc, PARAM_OUT)
    ok_in  = _get_or_create_room_int_param(doc, PARAM_IN)

    # Single transaction for all writes
    t = Transaction(doc, "Write room corner counts (outward/inward)")
    t.Start()

    failures = 0
    total_corners_sum = 0

    for room in target_rooms:
        try:
            #outc, inc, totalc = count_room_corners_split(room, SpatialElementBoundaryLocation.Finish)
            outc, inc, totalc = count_room_corners_split_with_holes(room, SpatialElementBoundaryLocation.Finish)
            total_corners_sum += totalc

            # Safe room number / name
            rmnum = "?"
            pnum = room.get_Parameter(BuiltInParameter.ROOM_NUMBER)
            if pnum: rmnum = pnum.AsString() or rmnum
            rmname = "<unnamed>"
            pname = room.get_Parameter(BuiltInParameter.ROOM_NAME)
            if pname: rmname = pname.AsString() or rmname

            # Writes
            if ok_out:
                p_out = room.LookupParameter(PARAM_OUT)
                if p_out and p_out.StorageType == StorageType.Integer:
                    p_out.Set(int(outc))
            if ok_in:
                p_in = room.LookupParameter(PARAM_IN)
                if p_in and p_in.StorageType == StorageType.Integer:
                    p_in.Set(int(inc))

            print('- Room {} "{}": {} corners ({} outward, {} inward)'.format(rmnum, rmname, totalc, outc, inc))
        except Exception as ex:
            failures += 1
            print("- Room <id {}>: ERROR ({})".format(room.Id, ex))

    t.Commit()

    if failures:
        print("Completed with {} error(s).".format(failures))

if __name__ == "__main__":
    main()
