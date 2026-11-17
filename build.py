#!/usr/bin/env python3
"""Build de la app ESTIMAT.

Fuente única en src/:
  src/app.html       plantilla de la app (en español), con marcas {{t:kNNNN}}, {{REDIRECT}} y {{DARK_HEAD}}
  src/i18n.json      diccionario de textos de la interfaz: {"kNNNN": {"es": ..., "pt": ...}}
  src/redirect.html  script inicial que redirige según idioma y tema ({{SELF}} = nombre del archivo)
  src/oscuro.json    tema oscuro: "head" (lo que se agrega al <head>) y "colores" (claro -> oscuro)

Genera: index.html (ES), pt.html (PT), oscuro.html (ES oscuro), pt-oscuro.html (PT oscuro).

Uso:  python3 build.py              # escribe los 4 archivos junto a build.py
      python3 build.py --check [DIR]  # prueba de equivalencia contra los HTML de DIR (por defecto, la raíz)
      python3 build.py --out DIR  # los escribe en DIR
      python3 build.py --artefacto --out DIR  # solo artefacto.html (ES, sin redirección) para el artefacto de Claude
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')

SALIDAS = [  # (archivo, idioma, oscuro)
    ('index.html', 'es', False),
    ('pt.html', 'pt', False),
    ('oscuro.html', 'es', True),
    ('pt-oscuro.html', 'pt', True),
]


def leer(nombre):
    with open(os.path.join(SRC, nombre), encoding='utf-8') as f:
        return f.read()


def cargar():
    return {
        'plantilla': leer('app.html'),
        'i18n': json.loads(leer('i18n.json')),
        'redirect': leer('redirect.html'),
        'oscuro': json.loads(leer('oscuro.json')),
    }


def regex_colores(mapa):
    # Una sola pasada, claves largas primero. Un color hex no debe seguir en otro dígito hex
    # (así #fff no toca #fffffe, que existe justamente para conservar el blanco real).
    partes = []
    for k in sorted(mapa, key=len, reverse=True):
        partes.append(re.escape(k) + (r'(?![0-9a-fA-F])' if k.startswith('#') else ''))
    return re.compile('|'.join(partes))


def render(fuente, idioma, oscuro, archivo):
    i18n = fuente['i18n']
    faltan = []

    def tx(m):
        k = m.group(1)
        if k not in i18n:
            faltan.append(k)
            return m.group(0)
        return i18n[k][idioma]

    s = re.sub(r'\{\{t:(k\d+)\}\}', tx, fuente['plantilla'])
    if faltan:
        raise SystemExit('Claves sin traducción en i18n.json: ' + ', '.join(sorted(set(faltan))))
    s = s.replace('{{REDIRECT}}', fuente['redirect'].replace('{{SELF}}', archivo), 1)
    s = s.replace('{{DARK_HEAD}}', fuente['oscuro']['head'] if oscuro else '', 1)
    if oscuro:
        mapa = fuente['oscuro']['colores']
        s = regex_colores(mapa).sub(lambda m: mapa[m.group(0)], s)
    if '{{' in s and re.search(r'\{\{(t:k\d+|REDIRECT|DARK_HEAD|SELF)\}\}', s):
        raise SystemExit('Quedaron marcas sin reemplazar en ' + archivo)
    return s


def artefacto(fuente):
    """Versión para el artefacto de Claude: ES claro, sin el script de redirección."""
    f = dict(fuente, redirect='')
    return render(f, 'es', False, 'index.html')


def construir():
    fuente = cargar()
    return {a: render(fuente, idioma, osc, a) for a, idioma, osc in SALIDAS}


def comparar(dir_ref):
    """Prueba de equivalencia: compara lo generado con los HTML que hay en dir_ref."""
    import difflib
    corte = lambda s: re.sub(r'(>)(?=<)|(;)|(")', lambda m: m.group(0) + '\n', s).split('\n')
    ok = True
    for nombre, html in construir().items():
        ruta = os.path.join(dir_ref, nombre)
        if not os.path.exists(ruta):
            print('falta', nombre); ok = False; continue
        with open(ruta, encoding='utf-8', newline='') as f:
            ref = f.read()
        if ref == html:
            print('igual  ', nombre)
            continue
        ok = False
        d = [l for l in difflib.unified_diff(corte(ref), corte(html), 'actual', 'generado', n=0, lineterm='')
             if l[:1] in '+-' and l[:3] not in ('+++', '---')]
        print('DISTINTO', nombre, '-', len(d), 'fragmentos cambiados; primeros:')
        for l in d[:12]:
            print('   ', l[:140])
    return ok


def main():
    out = ROOT
    if '--check' in sys.argv:
        ref = sys.argv[sys.argv.index('--check') + 1] if len(sys.argv) > sys.argv.index('--check') + 1 else ROOT
        sys.exit(0 if comparar(ref) else 1)
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
    if '--artefacto' in sys.argv:
        os.makedirs(out, exist_ok=True)
        dest = os.path.join(out, 'artefacto.html')
        with open(dest, 'w', encoding='utf-8', newline='') as f:
            f.write(artefacto(cargar()))
        print('ok artefacto.html (ES, sin redirección)')
        return
    os.makedirs(out, exist_ok=True)
    for nombre, html in construir().items():
        with open(os.path.join(out, nombre), 'w', encoding='utf-8', newline='') as f:
            f.write(html)
        print('ok', nombre, len(html.encode('utf-8')), 'bytes')


if __name__ == '__main__':
    main()
