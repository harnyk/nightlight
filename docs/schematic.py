"""Принципиальная схема ночника (schemdraw). Запуск: python3 docs/schematic.py
Результат: docs/img/schematic.svg и docs/img/schematic.png
"""
from pathlib import Path
import schemdraw
import schemdraw.elements as elm

OUT = Path(__file__).resolve().parent / "img"
OUT.mkdir(exist_ok=True)
schemdraw.config(fontsize=11, lw=1.3)
FS = 10


def block(d, x0, y0, w, h, title, left=(), right=(), stub=1.0):
    """Прямоугольный модуль. left/right: [(имя, y)], возвращает {имя: конец вывода}."""
    d += elm.Line().at((x0, y0)).to((x0 + w, y0))
    d += elm.Line().to((x0 + w, y0 + h))
    d += elm.Line().to((x0, y0 + h))
    d += elm.Line().to((x0, y0))
    d += elm.Label().at((x0 + w / 2, y0 + h + 0.15)).label(title, valign="bottom", fontsize=11)
    pins = {}
    for name, y in left:
        d += elm.Line().at((x0, y)).left(stub)
        d += elm.Label().at((x0 + 0.15, y)).label(name, halign="left", fontsize=FS)
        pins[name] = (x0 - stub, y)
    for name, y in right:
        d += elm.Line().at((x0 + w, y)).right(stub)
        d += elm.Label().at((x0 + w - 0.15, y)).label(name, halign="right", fontsize=FS)
        pins[name] = (x0 + w + stub, y)
    return pins


with schemdraw.Drawing(show=False) as d:
    d.config(unit=2.0)

    # ---------------- U1: XIAO nRF52840 ----------------
    u1 = block(d, 7, 0, 4, 6, "U1  Seeed XIAO nRF52840",
               left=[("BAT+", 4), ("BAT−", 2)],
               right=[("D0", 5), ("D1", 4), ("D2", 3), ("3V3", 2), ("GND", 1)])
    d += elm.Label().at((9, 0.6)).label("USB-C:\nпрошивка,\nзарядка\n50/100 мА", fontsize=8, valign="bottom")

    # ---------------- питание ----------------
    d += elm.Line().at(u1["BAT+"]).left(1.0)
    d += elm.Dot()
    vb = d.here
    d += elm.Vdd().label("VBAT", fontsize=FS)
    d += elm.Switch().at(vb).left(2.4).label("SW1 (опц.)\nSS12D00", fontsize=9)
    d += elm.Line().left(0.6)
    d += elm.Dot(open=True).label("J1.1", loc="top", fontsize=9)
    d += elm.Battery().down(3.0).reverse().label("BT1\nLiPo 603450\n3.7 В, 1000–1200 мА·ч\nс платой защиты",
                                                 loc="bottom", ofst=0.2, fontsize=9)
    d += elm.Dot(open=True).label("J1.2", loc="left", fontsize=9)
    d += elm.Line().down(0.5)
    d += elm.Ground()
    d += elm.Label().at((d.here[0] - 1.0, 2.5)).label("J1\nJST-PH\n2.0", halign="right", fontsize=9)
    d += elm.Line().at(u1["BAT−"]).left(0.8)
    d += elm.Ground()

    # ---------------- лента ----------------
    led = block(d, 23, 7, 4, 3.2, "LED1  SK6812 RGBW, 18 пикс.",
                left=[("+5V", 9.6), ("DIN", 8.6), ("GND", 7.6)])

    # D0 -> R3 -> DIN
    d += elm.Line().at(u1["D0"]).right(1.0)
    d += elm.Line().toy(led["DIN"][1])
    d += elm.Line().right(1.5).label("DATA", loc="top", fontsize=9)
    d += elm.Resistor().right(3.0).label("R3  330 Ом", fontsize=FS)
    d += elm.Line().to(led["DIN"])

    # +5V = VBAT, C1 между +5V и LED−
    d += elm.Line().at(led["+5V"]).left(2.0)
    d += elm.Dot()
    cp = d.here
    d += elm.Vdd().label("VBAT", fontsize=FS)
    d += elm.Capacitor(polar=True).at(cp).down().toy(5.6).label("C1\n220 мкФ\n6.3 В", loc="top", fontsize=FS)
    cn = d.here
    lneg = (led["GND"][0] - 0.8, 5.6)
    d += elm.Line().at(led["GND"]).left(0.8)
    d += elm.Line().toy(lneg[1])
    d += elm.Line().at(cn).to(lneg)
    d += elm.Dot().at(lneg).label("LED−", loc="right", fontsize=9)

    # ---------------- Q1 low-side ----------------
    q1 = elm.NFet().anchor("drain").at(lneg).reverse().label("Q1\nIRLB8721\n(IRLZ44N)", loc="right", fontsize=FS)
    d += q1
    d += elm.Line().at(q1.source).down(0.8)
    d += elm.Dot()
    sg = d.here
    d += elm.Ground()
    gn = (q1.gate[0] - 1.6, q1.gate[1])
    d += elm.Line().at(q1.gate).to(gn)
    d += elm.Dot()
    d += elm.Resistor().at(gn).down().toy(sg[1]).label("R2\n100 кОм", loc="bottom", fontsize=FS)
    d += elm.Line().to(sg)
    d += elm.Resistor().at(gn).left(3.0).label("R1  100 Ом", fontsize=FS)
    d += elm.Line().tox(u1["D1"][0] + 2.0)
    d += elm.Line().toy(u1["D1"][1])
    d += elm.Line().to(u1["D1"]).label("LED_EN", loc="top", fontsize=9)

    # ---------------- U2: TTP223 ----------------
    u2 = block(d, 16, -3.5, 3, 3, "U2  TTP223 (модуль)",
               left=[("OUT", -1.0), ("VCC", -2.0), ("GND", -3.0)], right=[("PAD", -2.0)])
    d += elm.Line().at(u1["D2"]).right(2.5)
    d += elm.Line().toy(u2["OUT"][1])
    d += elm.Line().to(u2["OUT"]).label("TOUCH", loc="top", fontsize=9)
    d += elm.Line().at(u1["3V3"]).right(1.5)
    d += elm.Line().toy(u2["VCC"][1])
    d += elm.Line().to(u2["VCC"])
    d += elm.Line().at(u2["GND"]).left(0.6)
    d += elm.Ground()
    d += elm.Line().at(u1["GND"]).right(0.6)
    d += elm.Ground()
    d += elm.Line().at(u2["PAD"]).right(1.0)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 0.3, d.here[1])).label("E1  сенсор: медная фольга\n20×6 мм за стенкой 1.2 мм",
                                                          halign="left", fontsize=9)

    # ---------------- примечания ----------------
    d += elm.Label().at((-1.5, -5.0)).label(
        "Примечания\n"
        "1. Лента питается напрямую от LiPo (3.0–4.2 В); на малой яркости SK6812 работает до ~3.5 В.\n"
        "2. Q1 — ключ в минусе ленты. Перед LED_EN = 0 перевести D0 в LOW, иначе лента питается через DIN.\n"
        "3. Ток покоя ленты ~0.5–1 мА на пиксель — в выключенном состоянии лента обесточена Q1.\n"
        "4. Зарядка 100 мА: P0.13 = LOW (по умолчанию 50 мА). Назначение D0/D1/D2 — предварительное.",
        halign="left", valign="top", fontsize=9)

    d.save(str(OUT / "schematic.svg"))
    d.save(str(OUT / "schematic.png"), dpi=150)
print("ok")
