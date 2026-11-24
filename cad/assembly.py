import cadquery as cq
import paths
paths.enter_out()
from stand import body, lid, Z_SHELF, Z_DIFF, Z_GLASS, LID_T, XIAO_CX, BAT_CX, CAV_W

from pathlib import Path

def load(n): return cq.importers.importStep(f"components/{n}.step").val()

# официальная модель Seeed, если сгенерирована (make xiao), иначе габаритная
XIAO_MODEL = "xiao_nrf52840_seeed" if Path("components/xiao_nrf52840_seeed.step").exists() else "xiao_nrf52840"

def place(shape, rot=None, pos=(0, 0, 0), zmin=None):
    s = shape
    if rot:
        for axis, ang in rot:
            s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(*axis), ang)
    if zmin is not None:
        s = s.translate(cq.Vector(0, 0, zmin - s.BoundingBox().zmin))
    return s.translate(cq.Vector(*pos))

alu = cq.Workplane("XY").box(125, 12, 0.8, centered=(True, True, False)).val()
diff = cq.Workplane("XY").box(130, 20, 2, centered=(True, True, False)).edges("|Z").fillet(1.0).val()

def real(n): return cq.importers.importStep(f"components/real/{n}.step").val()

# раскладка отсека электроники (X вдоль подставки, USB-C XIAO в -X)
MOS_X, MOS_Y = -38.0, 11.0      # выход ножек MOSFET из корпуса
BAT_X = BAT_CX + 2.5            # центр банки LiPo

parts = {
    "glass":    (place(load("glass_block"), pos=(0, 0, Z_GLASS)), (0.7, 0.85, 0.95, 0.35)),
    "diffuser": (place(diff, pos=(0, 0, Z_DIFF)), (1, 1, 0.92, 0.8)),
    "alu":      (place(alu, pos=(0, 0, Z_SHELF)), (0.6, 0.6, 0.62, 1)),
    "strip":    (place(real("led_strip_sk6812_18px_real"), pos=(0, 0, Z_SHELF + 0.8)), (0.95, 0.95, 0.95, 1)),
    "xiao":     (place(load(XIAO_MODEL), rot=[((0, 0, 1), 180)], pos=(XIAO_CX, 0, 0), zmin=LID_T), (0.1, 0.45, 0.2, 1)),
    "battery":  (place(real("lipo_603450_real"), pos=(BAT_X, 0, 0), zmin=LID_T), (0.75, 0.75, 0.78, 1)),
    "jst":      (place(real("jst_ph2_pair"), pos=(-8.0, 0, 0), zmin=LID_T), (0.95, 0.95, 0.9, 1)),
    "mosfet":   (place(real("mosfet_to220_flat"), pos=(MOS_X, MOS_Y, 0), zmin=LID_T), (0.12, 0.12, 0.12, 1)),
    "r_gate":   (place(real("resistor_0207_flat"), pos=(-44.0, 3.0, 0), zmin=LID_T), (0.8, 0.7, 0.5, 1)),
    "r_pull":   (place(real("resistor_0207_flat"), pos=(-33.0, 0.5, 0), zmin=LID_T), (0.8, 0.7, 0.5, 1)),
    "r_data":   (place(real("resistor_0207_flat"), pos=(-45.0, -12.0, 0), zmin=LID_T), (0.8, 0.7, 0.5, 1)),
    "cap":      (place(real("cap_radial_6x7_flat"), pos=(-6.0, 11.0, 0), zmin=LID_T), (0.15, 0.3, 0.8, 1)),
    "ttp223":   (place(real("ttp223_module"), pos=(-6.0, -11.0, 0), zmin=LID_T), (0.2, 0.3, 0.75, 1)),
    "touch":    (place(cq.Workplane("XY").box(20, 0.1, 6, centered=(True, True, False)).val(),
                       pos=(0, -CAV_W/2 - 1.25, LID_T + 0.5)), (0.85, 0.5, 0.2, 1)),
}

B, Ld = body.val(), lid.val()

def _bb_overlap(a, b, tol=0.01):
    A, C = a.BoundingBox(), b.BoundingBox()
    return not (A.xmax < C.xmin - tol or C.xmax < A.xmin - tol or A.ymax < C.ymin - tol or
                C.ymax < A.ymin - tol or A.zmax < C.zmin - tol or C.zmax < A.zmin - tol)

def overlap(a, b):
    """Объём пересечения по отдельным солидам (сложные чужие STEP иначе ломают булевы операции)."""
    v, failed = 0.0, 0
    for sa in a.Solids():
        for sb in b.Solids():
            if not _bb_overlap(sa, sb):
                continue
            try:
                v += sa.intersect(sb).Volume()
            except Exception:
                failed += 1
    return v, failed
print(f"XIAO: {XIAO_MODEL}")
print("Проверка пересечений (мм³):")
names = list(parts)
for n in names:
    s = parts[n][0]
    for other, os_ in [("корпус", B), ("крышка", Ld)] + [(m, parts[m][0]) for m in names if m > n]:
        v, failed = overlap(s, os_)
        if v > 0.01:
            print(f"  ! {n} × {other}: {v:.2f}")
        if failed:
            print(f"  ? {n} × {other}: {failed} пар солидов не удалось проверить")
print("готово")

asm = cq.Assembly(name="nightlight_stand")
asm.add(body, name="body", color=cq.Color(0.2, 0.2, 0.22, 1))
asm.add(lid, name="lid", color=cq.Color(0.3, 0.3, 0.32, 1))
for n, (s, c) in parts.items():
    asm.add(cq.Workplane().add(s), name=n, color=cq.Color(*c))
asm.save("nightlight_stand_assembly.step")
