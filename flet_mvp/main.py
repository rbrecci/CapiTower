"""CapiTower MVP em Flet.

Desktop:   python main.py         (ou: flet run main.py)
Celular:   flet run --android     (ou --ios) e escaneia o QR code no app Flet
Navegador: flet run --web main.py
"""

import flet as ft

from capitower.ui import main

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
