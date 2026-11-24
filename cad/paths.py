"""Все скрипты пишут результаты в ../exports (относительно этой папки)."""
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "exports"

def enter_out():
    OUT.mkdir(exist_ok=True)
    os.chdir(OUT)
