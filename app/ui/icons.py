"""Offline SVG outline icons, rendered by QtSvg at multiple resolutions."""
from functools import lru_cache
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

PATHS={
'dashboard':'<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="4" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="11" width="7" height="10" rx="1.5"/>',
'building':'<path d="M4 21V7l8-4 8 4v14M2 21h20M9 21v-5h6v5M8 9h1m6 0h1M8 12h1m6 0h1"/>',
'people':'<circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3m1-17a3 3 0 0 1 0 6m2 4a5 5 0 0 1 3 5v2"/>',
'process':'<rect x="3" y="3" width="7" height="6" rx="1"/><rect x="14" y="15" width="7" height="6" rx="1"/><path d="M17 15V6h-7M7 9v9h7m-3-3 3 3-3 3"/>',
'chart':'<path d="M3 3v18h18M7 16v-4m5 4V7m5 9v-6"/>',
'shield':'<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/>',
'risk':'<path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v5m0 3h.01"/>',
'matrix':'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18m6-18v18M3 9h18M3 15h18"/>',
'plan':'<path d="M7 3h10v3H7zM7 5H4v16h16V5h-3M8 11h8M8 15h8M8 18h5"/>',
'recovery':'<path d="M3 10a9 9 0 1 1 2 9M3 3v7h7M12 7v5l3 2"/>',
'steps':'<path d="M9 5h12M9 12h12M9 19h12M3 5h1M3 12h1M3 19h1"/>',
'scenario':'<path d="m8 3 12 9-12 9V3Z"/>',
'report':'<path d="M14 2H5v20h14V7l-5-5v5h5M8 11h8M8 15h8M8 18h5"/>',
'export':'<path d="M12 3v12m-4-4 4 4 4-4M3 15v6h18v-6"/>',
'settings':'<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="9" cy="18" r="2"/>',
'lock':'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>',
'backup':'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/>',
'info':'<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10h.01"/>',
'search':'<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
'menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
'back':'<path d="m14 5-7 7 7 7"/>',
'forward':'<path d="m10 5 7 7-7 7"/>',
'plus':'<path d="M12 4v16M4 12h16"/>',
'eye':'<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
'eye-off':'<path d="m3 3 18 18M9 5a14 14 0 0 1 13 7l-4 4M6 6l-4 6s4 7 10 7l4-1M10 10l4 4"/>',
'check':'<path d="m4 12 5 5L20 6"/>',
'catalog':'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 9v12"/>',
'sun':'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1"/>',
}

@lru_cache(maxsize=128)
def icon(name,color='#087f7a'):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{PATHS.get(name,PATHS["info"])}</svg>'
    renderer=QSvgRenderer(QByteArray(svg.encode()))
    result=QIcon()
    for size in (20,24,32,48,64):
        pixmap=QPixmap(size,size);pixmap.fill(Qt.GlobalColor.transparent)
        painter=QPainter(pixmap);renderer.render(painter);painter.end()
        result.addPixmap(pixmap)
    return result
