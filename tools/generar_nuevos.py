#!/usr/bin/env python3
"""Genera los mapas nuevos con relleno de guia. Salida: nuevos.js"""
import random

def lienzo(w, h, base):
    return [[base] * w for _ in range(h)]

def rect(g, c, x, y, w, h):
    for j in range(y, y + h):
        for i in range(x, x + w):
            if 0 <= i < len(g[0]) and 0 <= j < len(g):
                g[j][i] = c

def borde(g, c, t=1):
    h, w = len(g), len(g[0])
    for j in range(h):
        for i in range(w):
            if i < t or j < t or i >= w - t or j >= h - t:
                g[j][i] = c

def lin(g, c, orient, fijo, a, b, gr=1):
    for k in range(a, b + 1):
        for d in range(gr):
            if orient == 'h':
                if 0 <= fijo + d < len(g) and 0 <= k < len(g[0]): g[fijo + d][k] = c
            else:
                if 0 <= k < len(g) and 0 <= fijo + d < len(g[0]): g[k][fijo + d] = c

def salida(g, c, lado, pos, largo=3):
    h, w = len(g), len(g[0])
    if lado == 'O':   g[pos][0] = 'E';     lin(g, c, 'h', pos, 1, largo)
    elif lado == 'E': g[pos][w-1] = 'E';   lin(g, c, 'h', pos, w-1-largo, w-2)
    elif lado == 'N': g[0][pos] = 'E';     lin(g, c, 'v', pos, 1, largo)
    elif lado == 'S': g[h-1][pos] = 'E';   lin(g, c, 'v', pos, h-1-largo, h-2)

def disp(g, c, n, sobre, semilla):
    r = random.Random(semilla)
    libres = [(i, j) for j in range(len(g)) for i in range(len(g[0])) if g[j][i] in sobre]
    r.shuffle(libres)
    for i, j in libres[:n]:
        g[j][i] = c

def filas(g):
    return [''.join(r) for r in g]


# ----------------------------------------------------------- cueva genérica
def cueva(w, h, roca, suelo, salidas, semilla, agua=None, pilares=True):
    """Sala de cueva con paredes, columnas de guía y salidas en los bordes."""
    g = lienzo(w, h, suelo)
    borde(g, roca, 2)
    if pilares:
        paso = max(5, w // 5)
        for y in range(4, h - 4, paso):
            for x in range(4, w - 4, paso):
                rect(g, roca, x, y, 2, 2)
    if agua:
        rect(g, agua, w // 3, h // 3, w // 3, h // 3)
    for lado, pos in salidas:
        salida(g, suelo, lado, pos)
    disp(g, 'x', max(3, w // 6), suelo, semilla)
    return filas(g)


MAPAS = {}

# --------------------------------------------------- Liga Nubia 40 x 40
g = lienzo(40, 40, '^')
rect(g, '#', 2, 2, 36, 36)
rect(g, '=', 4, 4, 32, 32)
for (x, y) in [(6, 6), (28, 6), (6, 28), (28, 28)]:      # cuatro salas del Alto Mando
    rect(g, '#', x, y, 6, 6)
    rect(g, 'L', x + 1, y + 1, 4, 4)
rect(g, 'n', 16, 14, 8, 12)                              # cumbre nevada central
rect(g, 'i', 18, 17, 4, 6)
lin(g, '=', 'v', 19, 4, 35, 2)
lin(g, '=', 'h', 19, 4, 35, 2)
salida(g, '=', 'S', 19, 4)
MAPAS['Liga Nubia'] = filas(g)

# --------------------------------------------------- interiores
g = lienzo(15, 25, '=')
borde(g, '#', 1)
for y in range(3, 21, 6):                                 # graderías enfrentadas
    rect(g, '#', 2, y, 3, 3)
    rect(g, '#', 10, y, 3, 3)
rect(g, 'L', 6, 10, 3, 5)                                 # tarima central
salida(g, '=', 'S', 7)
MAPAS['Liga de entrenadores'] = filas(g)

# --------------------------------------------------- guarida y cuevas
MAPAS['Guarida del Dorado 1'] = (lambda: (
    lambda g: (
        borde(g, '#', 2),
        rect(g, 'D', 9, 9, 7, 7),
        [rect(g, '#', x, y, 3, 3) for (x, y) in [(4, 4), (18, 4), (4, 18), (18, 18)]],
        lin(g, '=', 'v', 12, 2, 22),
        lin(g, '=', 'h', 12, 2, 22),
        salida(g, '=', 'S', 12, 3),
        salida(g, '=', 'N', 12, 3),
        filas(g))[-1])(lienzo(25, 25, '='))
)()

MAPAS['Cueva Descanso']                 = cueva(7, 7, '^', ',', [('S', 3)], 91, pilares=False)
MAPAS['Caverna Glaciar Subterranea 1']  = cueva(20, 20, '^', 'n', [('N', 10), ('S', 10)], 92, agua='i')
MAPAS['Caverna Glaciar Subterranea 2']  = cueva(20, 20, '^', 'n', [('N', 10), ('E', 10)], 93, agua='i')
MAPAS['Ruta 2.1 Rocosos']               = cueva(30, 25, '^', ',', [('O', 12), ('E', 12), ('N', 15)], 94, pilares=True)
MAPAS['Tunel de Mequejo']               = cueva(30, 30, '^', ',', [('O', 15), ('E', 15)], 95)
MAPAS['Cueva del lago Cañaveral 1']     = cueva(20, 20, '^', ',', [('N', 10), ('S', 10)], 96, agua='~')
MAPAS['Cueva del lago Cañaveral 2']     = cueva(20, 20, '^', ',', [('N', 10), ('O', 10)], 97, agua='~')
MAPAS['Cueva Rocosa Amurallada 1']      = cueva(30, 30, '^', ',', [('O', 15), ('E', 15)], 98)
MAPAS['Cueva Rocosa Amurallada 2']      = cueva(30, 30, '^', ',', [('N', 15), ('S', 15)], 99)

# ----------------------------------------------------------- salida
def js(f):
    return "[" + ",".join("'" + x + "'" for x in f) + "]"

with open('nuevos.js', 'w', encoding='utf-8') as fh:
    for k, v in MAPAS.items():
        fh.write(f" '{k}':{js(v)},\n")

print(f"{len(MAPAS)} mapas generados\n")
for k, v in MAPAS.items():
    anchos = {len(r) for r in v}
    ok = 'OK ' if len(anchos) == 1 else 'MAL'
    print(f"  {ok} {k:36s} {list(anchos)[0]:>3} x {len(v)}")
