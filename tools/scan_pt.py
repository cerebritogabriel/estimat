"""Escaneo de español filtrado en las pantallas PT de la app ESTIMAT.
Abre pt.html (y pt-oscuro.html) en Chrome headless, hace recorridos al azar por la interfaz
y busca en el texto visible y en aria-label/title/placeholder/alt palabras típicas del español.
Uso: python3 tools/scan_pt.py DIR_CON_LOS_HTML [paseos] [clics]"""
import sys,re,random,json,os
from playwright.sync_api import sync_playwright
D=os.path.abspath(sys.argv[1]); N=int(sys.argv[2]) if len(sys.argv)>2 else 25; K=int(sys.argv[3]) if len(sys.argv)>3 else 14
ES_W={'y','el','los','las','tus','tu','del','muy','pero','hoy','ayer','qué','cómo','cuándo','cuánto','también','ahora','aquí','hacia','puedes','tienes','eres','sí','usted','estás','hay','quieres','otro','otra','entre','sin','hasta','desde','mientras','cuando','donde','esto','eso','acción','acciones','meta','metas'}
ES_W-= {'meta','metas','entre','desde','otra','otro','sem','hoje'}  # existen igual en PT
PT_OK={'sim'}
RX=re.compile(r'[ñ¿¡]|ci[oó]n(es)?\b|\b('+'|'.join(sorted(ES_W))+r')\b',re.I)
JS="""()=>{const o=[document.body.innerText];document.querySelectorAll('[aria-label],[title],[placeholder],[alt]').forEach(e=>{for(const a of ['aria-label','title','placeholder','alt']){const v=e.getAttribute(a);if(v)o.push(v)}});return o.join('\\n')}"""
CL="""()=>{const v=[...document.querySelectorAll('button,a,summary,[data-go],[data-next],[data-pager],label,[role=button],input[type=radio],input[type=checkbox]')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&!e.disabled});return v.length}"""
hits={};seen=set()
def scan(txt,where):
    for line in txt.split('\n'):
        line=line.strip()
        if not line or line in seen: continue
        seen.add(line)
        m=RX.search(line)
        if m: hits.setdefault(line,where)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for page_name,theme in [('pt.html','light'),('pt-oscuro.html','dark')]:
        for w in range(N):
            random.seed(w*7+len(page_name))
            ctx=b.new_context(); pg=ctx.new_page()
            pg.add_init_script(f"try{{localStorage.setItem('estimat.lang','pt');localStorage.setItem('estimat.theme','{theme}')}}catch(e){{}}")
            pg.on('dialog',lambda d:d.dismiss())
            pg.goto('file://'+D+'/'+page_name); pg.wait_for_timeout(400)
            assert pg.evaluate("document.documentElement.lang").startswith('pt'), pg.url
            scan(pg.evaluate(JS),page_name+' inicio')
            for k in range(K):
                n=pg.evaluate(CL)
                if not n: break
                i=random.randrange(n)
                try:
                    pg.evaluate(f"""()=>{{const v=[...document.querySelectorAll('button,a,summary,[data-go],[data-next],[data-pager],label,[role=button],input[type=radio],input[type=checkbox]')].filter(e=>{{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&!e.disabled}});const e=v[{i}];if(e.tagName==='A'&&/^https?:/.test(e.getAttribute('href')||''))return;e.click()}}""")
                    pg.wait_for_timeout(120)
                    if not pg.url.startswith('file://'+D): break
                    scan(pg.evaluate(JS),f'{page_name} paseo {w} clic {k}')
                except Exception as ex: break
            ctx.close()
    b.close()
print('líneas únicas revisadas:',len(seen),'| candidatas:',len(hits))
for l,w in sorted(hits.items(),key=lambda x:x[1]): print('-',repr(l[:160]),'  @',w)
