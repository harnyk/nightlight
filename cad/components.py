"""Габаритные модели компонентов ночника. Единицы: мм.
Каждая деталь: низ на Z=0, центр по X/Y в 0 (кроме оговорённых).
Размеры — по типовым даташитам, с небольшим запасом. Перед финальной печатью сверить штангенциркулем.
"""
import cadquery as cq, os
import paths
paths.enter_out()
os.makedirs("components", exist_ok=True)
parts = {}

# --- Seeed XIAO nRF52840: плата 21 x 17.8 x 1.2, экран RF-модуля, USB-C выступает за край ---
pcb = cq.Workplane("XY").box(21, 17.8, 1.2, centered=(True, True, False)).edges("|Z").fillet(1.0)
shield = cq.Workplane("XY").box(12.5, 11.0, 2.0, centered=(True, True, False)).translate((-2.5, 0, 1.2))
usb = (cq.Workplane("XY").box(7.4, 9.0, 3.2, centered=(True, True, False))
       .edges("|X").fillet(1.2).translate((21/2 - 7.4/2 + 1.3, 0, 1.2)))   # USB-C смотрит в +X, выступ 1.3 мм
xiao = pcb.union(shield).union(usb)
parts["xiao_nrf52840"] = xiao

# --- LiPo 603450 (6 x 34 x 50) + зона сварного шва/платы защиты, запас на "набухание" ---
cell = cq.Workplane("XY").box(50, 34, 6.5, centered=(True, True, False)).edges("|Z").fillet(1.5)
pcm = cq.Workplane("XY").box(5, 30, 4.0, centered=(True, True, False)).translate((50/2 + 2.5, 0, 1.2))
lipo = cell.union(pcm)       # провода выходят в +X
parts["lipo_603450"] = lipo

# --- MOSFET TO-220 (IRLB8721 / IRLZ44N): корпус + теплоотвод-флажок + 3 вывода ---
body = cq.Workplane("XY").box(10.2, 4.5, 9.2, centered=(True, True, False))
tab = (cq.Workplane("XY").box(10.2, 1.3, 6.4, centered=(True, True, False))
       .translate((0, 4.5/2 - 1.3/2, 9.2))
       .faces(">Y").workplane().center(0, 9.2 + 6.4 - 2.8 - 9.2 - 3.2).hole(3.6))
to220 = body.union(tab)
for dx in (-2.54, 0, 2.54):
    to220 = to220.union(cq.Workplane("XY").box(0.8, 0.5, 13.0, centered=(True, True, False))
                        .translate((dx, 0, -13.0)))
parts["mosfet_to220"] = to220          # низ корпуса на Z=0, ножки вниз

# --- Лента SK6812 RGBW 144/м, 18 пикселей (124.9 мм), PCB 10 мм ---
N, pitch, W = 18, 1000/144, 10.0
L = N * pitch
strip = cq.Workplane("XY").box(L, W, 0.5, centered=(True, True, False))   # плата + скотч
for i in range(N):
    x = -L/2 + pitch/2 + i * pitch
    strip = strip.union(cq.Workplane("XY").box(5.0, 5.0, 1.6, centered=(True, True, False)).translate((x, 0, 0.5)))
parts["led_strip_sk6812_18px"] = strip

# --- Электролит 220 мкФ 6.3 В, радиальный 6.3 x 11 ---
cap = cq.Workplane("XY").circle(6.3/2).extrude(11.0)
for dx in (-1.25, 1.25):
    cap = cap.union(cq.Workplane("XY").center(dx, 0).circle(0.25).extrude(-10))
parts["cap_220uF_6x11"] = cap

# --- Рассеиватель: опаловый акрил 3 мм под 18 пикселей ---
parts["diffuser_opal_3mm"] = cq.Workplane("XY").box(128, 12, 3, centered=(True, True, False))

# --- Сенсорная площадка: медная фольга 15 x 15 ---
parts["touch_pad_foil"] = cq.Workplane("XY").box(15, 15, 0.1, centered=(True, True, False))

# --- Стеклянный блок (из прошлой модели) ---
glass = cq.importers.importStep("glass_block_envelope.step")
parts["glass_block"] = glass

colors = {"xiao_nrf52840": (0.1,0.45,0.2), "lipo_603450": (0.75,0.75,0.78), "mosfet_to220": (0.12,0.12,0.12),
          "led_strip_sk6812_18px": (0.95,0.95,0.95), "cap_220uF_6x11": (0.15,0.3,0.8), "diffuser_opal_3mm": (1,1,0.92),
          "touch_pad_foil": (0.85,0.5,0.2), "glass_block": (0.7,0.85,0.95)}

# экспорт по отдельности
for k, v in parts.items():
    cq.exporters.export(v, f"components/{k}.step")
    bb = v.val().BoundingBox()
    print(f"{k:24s} {bb.xlen:6.1f} x {bb.ylen:5.1f} x {bb.zlen:5.1f}")

# библиотека-раскладка: всё в одном STEP, детали разложены в ряд
asm = cq.Assembly(name="nightlight_components")
layout = {"glass_block": (0, 0, 0), "led_strip_sk6812_18px": (0, -45, 0), "diffuser_opal_3mm": (0, -65, 0),
          "lipo_603450": (-50, -110, 0), "xiao_nrf52840": (10, -110, 0), "mosfet_to220": (40, -110, 13),
          "cap_220uF_6x11": (60, -110, 10), "touch_pad_foil": (85, -110, 0)}
for k, pos in layout.items():
    asm.add(parts[k], name=k, loc=cq.Location(cq.Vector(*pos)), color=cq.Color(*colors[k]))
asm.save("nightlight_components_library.step")
