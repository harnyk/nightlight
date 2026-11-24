"""Реальные модели электронных компонентов.

Источники:
  * KiCad packages3D (cad/vendor/kicad, CC BY-SA 4.0 + исключение KiCad): TO-220, резисторы,
    электролит, светодиод SK6812, SOT-23-6, 0603.
  * Seeed Studio (cad/vendor/seeed): XIAO nRF52840 — см. xiao_seeed.py.
  * По даташитам/типовым чертежам (моделей производителя нет): модуль TTP223, пара JST-PH 2.0
    (PHR-2 + ответная вилка), плоский LiPo 603450, флекс-плата ленты.

Все детали: в собственных координатах, низ на Z=0. Результат: exports/components/real/*.step
"""
from pathlib import Path
import cadquery as cq
import paths

VENDOR = Path(__file__).resolve().parent / "vendor" / "kicad"
paths.enter_out()
OUT = Path("components/real")
OUT.mkdir(parents=True, exist_ok=True)


def kicad(name):
    return cq.importers.importStep(str(VENDOR / f"{name}.step")).val()


def rot(shape, *steps):
    for axis, ang in steps:
        shape = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(*axis), ang)
    return shape


def to_floor(shape, z=0.0):
    return shape.translate(cq.Vector(0, 0, z - shape.BoundingBox().zmin))


def box(lx, ly, lz, x=0, y=0, z=0):
    return cq.Workplane("XY").box(lx, ly, lz, centered=(True, True, False)).translate((x, y, z)).val()


parts = {}

# --- MOSFET TO-220, лёжа: флажок вниз, ножки в -X, выводы G-D-S вдоль Y -------------------
m = rot(kicad("TO-220-3_Vertical"), ((0, 1, 0), 90), ((1, 0, 0), -90))
bb = m.BoundingBox()
m = m.translate(cq.Vector(-bb.xmin - 9.75, -(bb.ymin + bb.ymax) / 2, -bb.zmin))   # X=0 — выход ножек из корпуса
parts["mosfet_to220_flat"] = m

# --- Резистор 0.25 Вт (DIN0207), лёжа, выводы отогнуты вбок (в +Y) --------------------------
r = rot(kicad("R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"), ((1, 0, 0), 90))
bb = r.BoundingBox()
r = r.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -bb.ymin - 1.25, -bb.zmin))    # центр корпуса в X=0,Y=0
parts["resistor_0207_flat"] = r

# --- Электролит ⌀6.3, лёжа, ось вдоль X, выводы в -X ----------------------------------------
c = rot(kicad("CP_Radial_D6.3mm_P2.50mm"), ((0, 1, 0), -90))
bb = c.BoundingBox()
c = c.translate(cq.Vector(-bb.xmax, -(bb.ymin + bb.ymax) / 2, -bb.zmin))           # торец корпуса в X=0
parts["cap_radial_6x7_flat"] = c

# --- Лента SK6812: флекс-плата 10 мм + 18 светодиодов 5050 + площадки --------------------
N, PITCH, W, T = 18, 1000 / 144, 10.0, 0.25
L = N * PITCH
led = kicad("LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm")
strip = cq.Workplane("XY").add(box(L, W, T))
for i in range(N):
    x = -L / 2 + PITCH / 2 + i * PITCH
    strip = strip.add(led.translate(cq.Vector(x, 0, T)))
for sx in (-1, 1):                         # медные площадки +5V / DIN / GND на концах
    for dy in (-3.0, 0.0, 3.0):
        strip = strip.add(box(1.6, 2.0, 0.05, sx * (L / 2 - 1.0), dy, T))
parts["led_strip_sk6812_18px_real"] = cq.Compound.makeCompound(strip.vals())

# --- Модуль TTP223 (типовой, 15 x 11 мм): плата, TTP223 в SOT-23-6, светодиод, R, C, 3 вывода --
pcb = cq.Workplane("XY").box(15, 11, 1.0, centered=(True, True, False)).edges("|Z").fillet(0.8)
pcb = pcb.faces(">Z").workplane().pushPoints([(-6.0, dy) for dy in (-2.54, 0, 2.54)]).hole(1.0)  # VCC / I/O / GND
ttp = [pcb.val(),
       kicad("SOT-23-6").translate(cq.Vector(1.5, 0, 1.0)),
       rot(kicad("LED_0603_1608Metric"), ((0, 0, 1), 90)).translate(cq.Vector(5.5, 3.0, 1.0)),
       kicad("R_0603_1608Metric").translate(cq.Vector(5.5, -1.0, 1.0)),
       kicad("R_0603_1608Metric").translate(cq.Vector(-2.5, 3.0, 1.0)),
       kicad("C_0603_1608Metric").translate(cq.Vector(-2.5, -3.0, 1.0)),
       box(13.0, 9.0, 0.035, 0.6, 0, -0.035)]          # сенсорная площадка на обороте
parts["ttp223_module"] = to_floor(cq.Compound.makeCompound(ttp))

# --- Пара JST-PH 2.0, 2 контакта: розетка PHR-2 + вилка, в сцепке (по даташиту JST PH) --------
phr = cq.Workplane("XY").box(6.0, 4.5, 4.5, centered=(False, True, False))          # PHR-2: 6.0 x 4.5 x 4.5
plug = cq.Workplane("XY").box(7.0, 5.3, 5.3, centered=(False, True, False)).translate((5.0, 0, -0.4))
plug = plug.cut(cq.Workplane("XY").box(6.0, 4.6, 4.6, centered=(False, True, False)).translate((5.0, 0, -0.05)))
wires = []
for dy in (-1.0, 1.0):
    for x0, x1 in ((-3.0, 0.0), (12.0, 15.0)):          # короткие хвосты проводов
        wires.append(cq.Workplane("YZ").center(dy, 2.25).circle(0.55).extrude(x1 - x0).translate((x0, 0, 0)).val())
jst = cq.Compound.makeCompound([phr.val(), plug.val()] + wires)
parts["jst_ph2_pair"] = to_floor(jst.translate(cq.Vector(-6.0, 0, 0)))  # стык розетка/вилка около X=0

# --- Плоский LiPo 603450: пакет с запаянным фланцем, плата защиты под каптоном, провода ----------
cell = cq.Workplane("XY").box(47.0, 34.0, 6.0, centered=(True, True, False)).edges("|Z").fillet(1.0)
cell = cell.edges(">Z").fillet(1.5)
flange = cq.Workplane("XY").box(3.0, 34.0, 1.0, centered=(True, True, False)).translate((-47 / 2 - 1.5, 0, 2.5))
pcm = cq.Workplane("XY").box(4.0, 26.0, 3.2, centered=(True, True, False)).translate((-47 / 2 - 3.0 - 2.0, 0, 1.4))
lipo_wires = [cq.Workplane("YZ").center(dy, 3.0).circle(0.6).extrude(-6.0).translate((-47 / 2 - 7.0, 0, 0)).val()
              for dy in (-1.5, 1.5)]
parts["lipo_603450_real"] = to_floor(cq.Compound.makeCompound([cell.val(), flange.val(), pcm.val()] + lipo_wires))

for k, v in parts.items():
    cq.exporters.export(cq.Workplane().add(v), str(OUT / f"{k}.step"))
    b = v.BoundingBox()
    print(f"{k:28s} X {b.xmin:7.2f}..{b.xmax:7.2f}  Y {b.ymin:6.2f}..{b.ymax:6.2f}  Z {b.zmin:5.2f}..{b.zmax:5.2f}")
