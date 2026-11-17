# Fuente de la app ESTIMAT

- `app.html`: la app en español, con marcas `{{t:kNNNN}}` donde el texto cambia en portugués.
- `i18n.json`: diccionario ES/PT de esas marcas.
- `redirect.html`: script inicial que elige archivo según `estimat.lang` y `estimat.theme`.
- `oscuro.json`: tema oscuro (agregado al `<head>` y reemplazo de colores). `#fffffe` existe para conservar el blanco real.

Para construir: `python3 build.py` (genera index.html, pt.html, oscuro.html, pt-oscuro.html).
Para comparar con lo publicado: `python3 build.py --check`.
Escaneo de español en PT: `python3 tools/scan_pt.py .` (necesita playwright y Chrome).
Al publicar, subir la versión de caché `V` en `sw.js`.
