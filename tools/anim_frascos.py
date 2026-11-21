"""Genera el SVG animado de la pantalla 31 de la presentación de la app ESTIMAT:
metas divididas que reciben ✓, cada ✓ cae como pelota en el frasco, y abajo el estante de frascos llenos.
Uso: python3 tools/anim_frascos.py  -> imprime el SVG (con marcas {{t:…}} para los textos)."""
import random

COL = ['#6bb0a7', '#3b70c0', '#875169', '#f5a097', '#7b7d55', '#efd49f', '#bf9268', '#8c4737']
JAR = ('M22 4h40M26 4v10C10 22 8 30 8 44v54a10 10 0 0 0 10 10h48a10 10 0 0 0 10-10V44'
       'c0-14-2-22-18-30V4')
R = 4.6


def pila(n, seed):
    """Posiciones (x, y) dentro del frasco (coordenadas 84x112), de abajo hacia arriba hasta el cuello.
    n=None devuelve el frasco completo."""
    rnd = random.Random(seed)
    out = []
    y, fila = 104 - R, 0
    while y > 6:
        if y >= 44: a, b = 9, 75
        elif y >= 14:
            f = (44 - y) / 30.0; a, b = 9 + f * 19, 75 - f * 19
        else: a, b = 27, 57
        k = max(1, int((b - a - (R if fila % 2 else 0)) // (2 * R)))
        x0 = (a + b) / 2 - (k - 1) * R + (R * .5 if fila % 2 else 0) * (1 if k > 3 else 0)
        for c in range(k):
            out.append((x0 + c * 2 * R + (rnd.random() - .5) * R * .5, y + (rnd.random() - .5)))
        y -= 2 * R - 1.4; fila += 1
    return out if n is None else out[:n]


def frasco(tx, ty, s, bolas, sw):
    g = '<g transform="translate(%g,%g) scale(%g)">' % (tx, ty, s)
    g += '<path d="%s" fill="rgba(253,251,249,.5)" stroke="#9a918a" stroke-width="%g" stroke-linejoin="round"/>' % (JAR, sw)
    for (x, y), c in bolas:
        g += '<circle cx="%.1f" cy="%.1f" r="%g" fill="%s"/>' % (x, y, R, c)
    return g + '</g>'


def svg():
    rnd = random.Random(7)
    W, H = 342, 300
    o = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="{{t:A11Y}}" '
         'style="display:block;max-width:100%%;height:auto;overflow:visible">' % (W, H, W, H)]
    # metas divididas
    filas = [(30, 0, 118), (74, 1, 92), (118, 3, 106), (162, 4, 84), (206, 6, 112)]
    t0, dt = 0.8, 1.0
    jx, jy, js = 226, 56, 1.1
    base = pila(None, 3)
    ini, nuevas = base[:-5], base[-5:]
    caen = []  # pelotas que caen en el frasco principal
    for i, (y, ci, ancho) in enumerate(filas):
        c = COL[ci]
        b = t0 + i * dt
        o.append('<rect x="8" y="%d" width="196" height="34" rx="12" fill="#fdfbf9" stroke="#ded5c7"/>' % (y - 17))
        o.append('<circle cx="26" cy="%d" r="6" fill="%s"/>' % (y, c))
        o.append('<rect x="40" y="%d" width="%d" height="8" rx="4" fill="#ece5da"/>' % (y - 4, ancho))
        o.append('<circle cx="184" cy="%d" r="9" fill="#fdfbf9" stroke="#c0b4a2" stroke-width="1.4"/>' % y)
        o.append('<path d="M179 %d l3.5 3.5 l6.5 -7" fill="none" stroke="#3f8f5c" stroke-width="2.2" '
                 'stroke-linecap="round" stroke-linejoin="round" pathLength="100" stroke-dasharray="100 100" '
                 'stroke-dashoffset="100"><animate class="fck" attributeName="stroke-dashoffset" from="100" to="0" dur=".3s" '
                 'begin="indefinite" fill="freeze"/></path>' % (y,))
        o.append('<rect data-pck="%d" x="8" y="%d" width="196" height="34" rx="12" fill="transparent" style="cursor:pointer"/>' % (i, y - 17))
        # la pelota sale del ✓ y cae en el frasco
        for j in range(1):
            sx, sy = nuevas[i + j]
            X, Y = jx + js * sx, jy + js * sy
            mx, my = jx + js * 42, jy - 8
            bj = b + .3 + j * .12
            caen.append('<circle class="fball" r="%.1f" fill="%s" opacity="0"><set attributeName="opacity" to="1" begin="indefinite" fill="freeze"/>'
                     '<animateMotion dur=".9s" begin="indefinite" fill="freeze" path="M184 %d Q%.0f %.0f %.1f %.1f L%.1f %.1f" '
                     'keyPoints="0;.55;1" keyTimes="0;.5;1" calcMode="linear"/></circle>'
                     % (R * js, COL[(ci + j) % 8] if j else c, y, (184 + mx) / 2, min(y, my) - 40, mx, my, X, Y))
    # frasco a la mitad
    fin = t0 + len(filas) * dt + .6
    k = (34 / 84) / js
    tx, ty = 8 + 4 * 42 - k * jx, 252 - k * jy
    o.append('<g>' + frasco(jx, jy, js, [(p, COL[rnd.randrange(8)]) for p in ini], 2) + ''.join(caen) +
             '<animateTransform class="fjar" attributeName="transform" type="translate" values="0,0;%.1f,%.1f" dur=".8s" begin="indefinite" fill="freeze"/>'
             '<animateTransform class="fjar" attributeName="transform" type="scale" additive="sum" values="1;%.3f" dur=".8s" begin="indefinite" fill="freeze"/>'
             '<animate class="fjarx" attributeName="opacity" from="1" to="0" dur=".2s" begin="indefinite" fill="freeze"/></g>'
             % (tx, ty, k))
    # estante con frascos llenos
    o.append('<text x="8" y="244" font-family="Open Sans,sans-serif" font-size="12" font-weight="600" fill="#9a918a">{{t:SHELF}}</text>')
    o.append('<path d="M8 300H334" stroke="#c0b4a2" stroke-width="2" stroke-linecap="round"/>')
    lleno = pila(None, 11)
    for k in range(5):
        g = frasco(0, 0, 34 / 84, [(p, COL[rnd.randrange(8)]) for p in lleno], 4)
        x = 8 + k * 42
        if k < 4:
            o.append('<g transform="translate(%d,252)">%s</g>' % (x, g))
        else:  # el quinto llega al final
            b = fin + .75
            o.append('<g transform="translate(%d,252)" opacity="0"><set class="fj5" attributeName="opacity" to="1" begin="indefinite" fill="freeze"/>'
                     '%s</g>' % (x, g))
    o.append('</svg>')
    return ''.join(o)


if __name__ == '__main__':
    print(svg())
