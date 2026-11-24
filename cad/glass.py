"""Габаритная модель стеклянного блока (парametric). Единицы: мм.
X — ширина (вид спереди), Y — толщина, Z — высота. Низ блока на Z=0, центр по X и Y в 0.
"""
import numpy as np, cadquery as cq
import paths
paths.enter_out()

# ---- параметры (снято с обрисовок по клетке 5 мм) ----
T        = 30.0     # толщина
LEFT_K   = 0.10     # наклон левой грани: x = LEFT_K*z
RIGHT_X0 = 138.9    # правая грань: x = RIGHT_X0 - RIGHT_K*z
RIGHT_K  = 0.162
TOP_Z0   = 93.4     # верх: z = TOP_Z0 + TOP_K*(x - TOP_X0)
TOP_X0   = 30.9
TOP_K    = 0.155
R = {"BL": 2.0, "BR": 5.0, "TR": 20.0, "TL": 16.0}   # радиусы углов профиля
EDGE_FILLET = 3.0   # скругление рёбер лицевой/задней грани

def inter(l1, l2):
    (p, d), (q, e) = l1, l2
    A = np.array([d, -e]).T
    t = np.linalg.solve(A, q - p)
    return p + t[0] * d

bottom = (np.array([0., 0.]), np.array([1., 0.]))
right  = (np.array([RIGHT_X0, 0.]), np.array([-RIGHT_K, 1.]))
top    = (np.array([TOP_X0, TOP_Z0]), np.array([1., TOP_K]))
left   = (np.array([0., 0.]), np.array([LEFT_K, 1.]))
V = {"BL": inter(left, bottom), "BR": inter(bottom, right),
     "TR": inter(right, top), "TL": inter(top, left)}
order = ["BL", "BR", "TR", "TL"]

def fillet(prev, v, nxt, r):
    a = (prev - v) / np.linalg.norm(prev - v)
    b = (nxt - v) / np.linalg.norm(nxt - v)
    ang = np.arccos(np.clip(a @ b, -1, 1))
    d = r / np.tan(ang / 2)
    p1, p2 = v + a * d, v + b * d
    bis = (a + b) / np.linalg.norm(a + b)
    c = v + bis * (r / np.sin(ang / 2))
    mid = c - bis * r
    return p1, mid, p2

arcs = [fillet(V[order[i-1]], V[k], V[order[(i+1) % 4]], R[k]) for i, k in enumerate(order)]
xmin = min(a[0][0] for a in arcs)  # для центрирования
xs = [p[0] for a in arcs for p in a]
cx = (max(xs) + min(xs)) / 2

def P(p): return (p[0] - cx, p[1])

w = cq.Workplane("XZ").moveTo(*P(arcs[0][2]))
for i in range(1, 5):
    p1, mid, p2 = arcs[i % 4]
    w = w.lineTo(*P(p1)).threePointArc(P(mid), P(p2))
w = w.close()
solid = w.extrude(T / 2, both=True)
if EDGE_FILLET > 0:
    solid = solid.faces(">Y or <Y").edges().fillet(EDGE_FILLET)

bb = solid.val().BoundingBox()
print("Габарит: X %.1f  Y %.1f  Z %.1f мм" % (bb.xlen, bb.ylen, bb.zlen))
print("Объём %.0f см3, масса (хрусталь ~3.0 г/см3) ≈ %.2f кг" % (solid.val().Volume()/1000, solid.val().Volume()/1000*3.0/1000))
cq.exporters.export(solid, "glass_block_envelope.step")
cq.exporters.export(solid, "glass_block_envelope.stl", tolerance=0.05, angularTolerance=0.1)
