"""Официальная модель XIAO nRF52840 (Seeed, CC BY-SA 4.0) -> наши координаты.
Вариант платы: XIAO_VARIANT=std (по умолчанию, обычная) или XIAO_VARIANT=plus.
В исходнике толщина платы идёт по +Y, USB-C смотрит в +X.
Результат: низ платы Z=0, центр платы X=Y=0, USB-C в +X (как у габаритной модели xiao_nrf52840.step).
"""
import os
from pathlib import Path
import cadquery as cq
import paths

FILES = {"std": "xiao-nrf52840-v3.step", "plus": "xiao-nrf52840-plus-v2.step"}
VARIANT = os.environ.get("XIAO_VARIANT", "std")
SRC = Path(__file__).resolve().parent / "vendor" / "seeed" / FILES[VARIANT]
paths.enter_out()

shape = cq.importers.importStep(str(SRC)).val()
shape = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)       # +Y -> +Z
pcb = max(shape.Solids(), key=lambda s: s.Volume()).BoundingBox()      # самый большой солид — плата
shape = shape.translate(cq.Vector(-(pcb.xmin + pcb.xmax) / 2, -(pcb.ymin + pcb.ymax) / 2, -pcb.zmin))

bb = shape.BoundingBox()
print(f"XIAO {VARIANT} (Seeed): " "X %.2f..%.2f  Y %.2f..%.2f  Z %.2f..%.2f" % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
Path("components").mkdir(exist_ok=True)
cq.exporters.export(cq.Workplane().add(shape), "components/xiao_nrf52840_seeed.step")
