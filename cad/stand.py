"""Подставка-ночник для стеклянного блока. Единицы: мм. X — длина, Y — глубина, Z — вверх.
Детали: корпус (печать вверх ногами, верхней гранью на стол) + нижняя крышка на 4 винтах M2.
"""
import cadquery as cq

# ---------- параметры ----------
L, W, H      = 149.0, 41.0, 24.0     # внешний габарит корпуса
R_PLAN       = 6.0                   # скругление углов в плане
GLASS_L, GLASS_W = 139.0, 31.0       # гнездо под стекло (стекло 137.8 x 30 + зазор)
POCKET_D     = 5.0                   # глубина гнезда
DIFF_L, DIFF_W, DIFF_T = 130.4, 20.4, 2.0   # ниша под опаловый акрил 130 x 20 x 2
CH_L, CH_W   = 126.0, 16.0           # световая камера под лентой
LID_T        = 1.6                   # толщина крышки
CAV_L, CAV_W, CAV_H = 144.0, 36.0, 7.2      # отсек электроники (над крышкой)
SHELF_T      = 1.2                   # полка, на которой лежит лента
BOSS_X, BOSS_Y = 68.5, 14.5          # винты M2

Z_CAV_TOP = LID_T + CAV_H                    # 8.8  потолок отсека
Z_SHELF   = Z_CAV_TOP + SHELF_T              # 10.0 пол световой камеры
Z_GLASS   = H - POCKET_D                     # 19.0 низ стекла
Z_DIFF    = Z_GLASS - DIFF_T                 # 17.0 низ рассеивателя

def rbox(l, w, h, r, z0=0.0):
    b = cq.Workplane("XY").box(l, w, h, centered=(True, True, False))
    if r > 0:
        b = b.edges("|Z").fillet(r)
    return b.translate((0, 0, z0))

# ---------- корпус ----------
body = rbox(L, W, H, R_PLAN)
body = body.faces(">Z").edges().fillet(2.0)
body = body.faces("<Z").edges().chamfer(0.6)

body = body.cut(rbox(GLASS_L, GLASS_W, POCKET_D + 1, 3.0, Z_GLASS))           # гнездо стекла
body = body.cut(rbox(DIFF_L, DIFF_W, DIFF_T + 0.01, 1.0, Z_DIFF))             # ниша рассеивателя
body = body.cut(rbox(CH_L, CH_W, Z_DIFF - Z_SHELF + 0.01, 1.0, Z_SHELF))      # световая камера
# фаска-заходник на кромке гнезда
body = body.cut(cq.Workplane("XY").rect(GLASS_L + 1.6, GLASS_W + 1.6).workplane(offset=-0.8)
                .rect(GLASS_L, GLASS_W).loft().translate((0, 0, H)))

body = body.cut(rbox(L - 3.0, W - 3.0, LID_T, R_PLAN - 1.5))                  # фальц под крышку
body = body.cut(rbox(CAV_L, CAV_W, Z_CAV_TOP - LID_T, 3.5, LID_T))            # отсек электроники

# бобышки под винты (M2 саморез, отверстие 1.7)
for sx in (-1, 1):
    for sy in (-1, 1):
        boss = cq.Workplane("XY").center(sx*BOSS_X, sy*BOSS_Y).circle(3.0).extrude(Z_CAV_TOP - LID_T).translate((0, 0, LID_T))
        body = body.union(boss)
        body = body.cut(cq.Workplane("XY").center(sx*BOSS_X, sy*BOSS_Y).circle(0.85).extrude(6.5).translate((0, 0, LID_T)))

# прижим XIAO сверху (давит на экран RF-модуля)
XIAO_CX = -61.2
body = body.union(cq.Workplane("XY").box(8, 8, Z_CAV_TOP - 5.0, centered=(True, True, False)).translate((XIAO_CX + 2.5, 0, 5.0)))

# проход проводов из камеры в отсек (над XIAO)
body = body.cut(cq.Workplane("XY").box(5, 6, SHELF_T + 0.2, centered=(True, True, False)).translate((-47, 0, Z_CAV_TOP - 0.1)))

# окно USB-C в торце (-X) + углубление под штекер снаружи
usb_z = LID_T + 1.2 + 1.6
body = body.cut(cq.Workplane("YZ").center(0, usb_z).rect(9.6, 4.0).extrude(-10).translate((-L/2 + 6, 0, 0)).edges("|X").fillet(1.5))
body = body.cut(cq.Workplane("YZ").center(0, usb_z).rect(12.8, 7.0).extrude(-1.2).translate((-L/2 + 1.2 - 0.0, 0, 0)).edges("|X").fillet(2.5))

# сенсорная зона на передней стенке (-Y): изнутри стенка утончена до ~1.2 мм под фольгу, снаружи кольцо-метка
wall = (W - CAV_W) / 2                      # 2.5
body = body.cut(cq.Workplane("XY").box(22, wall - 1.2, 6.6, centered=(True, False, False))
                .translate((0, -CAV_W/2 - (wall - 1.2), LID_T + 0.3)))
ring = (cq.Workplane("XZ").center(0, 5.2).circle(4.0).circle(3.2).extrude(0.4)
        .translate((0, -W/2 + 0.4, 0)))
body = body.cut(ring)

# ---------- крышка ----------
lid = rbox(L - 3.4, W - 3.4, LID_T, R_PLAN - 1.7)
for sx in (-1, 1):
    for sy in (-1, 1):
        lid = lid.cut(cq.Workplane("XY").center(sx*BOSS_X, sy*BOSS_Y).circle(1.15).extrude(LID_T))
        lid = lid.cut(cq.Solid.makeCone(2.2, 1.1, 1.1, pnt=cq.Vector(sx*BOSS_X, sy*BOSS_Y, -0.001)))   # потай
        # углубления под резиновые ножки (8 мм)
        lid = lid.cut(cq.Workplane("XY").center(sx*(BOSS_X - 10), sy*BOSS_Y).circle(4.2).extrude(0.6))
# направляющие для XIAO (3 стороны, USB-сторона открыта)
x0, x1, yh = -71.7, -50.7, 17.8/2
rail_h = 1.2
for (cx, cy, lx, ly) in [((x0+x1)/2, yh+0.8, x1-x0, 1.2), ((x0+x1)/2, -yh-0.8, x1-x0, 1.2), (x1+0.9, 0, 1.2, 17.8+2.8)]:
    lid = lid.union(cq.Workplane("XY").box(lx, ly, rail_h, centered=(True, True, False)).translate((cx, cy, LID_T)))
# бортики для аккумулятора 603450
BAT_CX = 35.5
for (cx, cy, lx, ly) in [(BAT_CX - 27.5 + 6, 17.0 + 0.8, 12, 1.2), (BAT_CX - 27.5 + 6, -17.0 - 0.8, 12, 1.2),
                         (BAT_CX + 20, 17.0 + 0.8, 12, 1.2), (BAT_CX + 20, -17.0 - 0.8, 12, 1.2),
                         (BAT_CX + 27.5 + 0.9, 0, 1.2, 20)]:
    lid = lid.union(cq.Workplane("XY").box(lx, ly, 2.0, centered=(True, True, False)).translate((cx, cy, LID_T)))

if __name__ == "__main__":
    import paths
    paths.enter_out()
    cq.exporters.export(body, "stand_body.step")
    cq.exporters.export(body, "stand_body.stl", tolerance=0.03, angularTolerance=0.1)
    cq.exporters.export(lid, "stand_lid.step")
    cq.exporters.export(lid, "stand_lid.stl", tolerance=0.03, angularTolerance=0.1)
    print("Z: потолок отсека %.1f, полка %.1f, рассеиватель %.1f, стекло %.1f" % (Z_CAV_TOP, Z_SHELF, Z_DIFF, Z_GLASS))
