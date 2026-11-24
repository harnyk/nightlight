# KiCad 3D models

Unmodified STEP files from the KiCad 3D library (`kicad-packages3D`, GitHub mirror, commit b8b3cfd):

| File | Used for |
|---|---|
| `TO-220-3_Vertical.step` | MOSFET IRLB8721 / IRLZ44N |
| `R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal.step` | 0.25 W resistors (100 Ω, 100 kΩ, 330 Ω) |
| `CP_Radial_D6.3mm_P2.50mm.step` | 220 µF electrolytic |
| `LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm.step` | LEDs of the SK6812 strip |
| `SOT-23-6.step`, `LED_0603_1608Metric.step`, `R_0603_1608Metric.step`, `C_0603_1608Metric.step` | parts of the TTP223 module |

License: CC BY-SA 4.0 with the KiCad library exception — see `LICENSE.md`.
`cad/parts_real.py` only re-orients them and combines them into assemblies (strip, TTP223 module).
