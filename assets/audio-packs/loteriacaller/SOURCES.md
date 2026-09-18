# Grabaciones extraídas de LoteriaCaller

- Fuente: https://www.loteriacaller.com/
- Catálogo público: https://www.loteriacaller.com/js/cards.js
- Lógica de selección de audio: https://www.loteriacaller.com/js/app.js
- Consulta y descarga: 18 de septiembre de 2026.
- La interfaz identifica sus grabaciones como audio pregenerado con Amazon Polly. No publica aquí el nombre exacto de las voces; no se le atribuye un locutor inferido.
- Se descargaron 180 MP3 originales sin procesamiento: 60 nombres en español, 60 nombres en inglés y 60 dichos en español. Cada conjunto contiene 54 cartas clásicas y 6 modernas adicionales.
- Rutas servidas: `audio/es/{id}.mp3`, `audio/en/{id}.mp3`, `audio/dicho/{id}.mp3`.
- Las rutas opcionales `audio/{es|en}/num-{numero}.mp3` respondieron HTTP 403 para los 120 archivos. No se intentó eludir esa respuesta. No se incluyen grabaciones de números.
- El selector de voces adicional se alimenta de `speechSynthesis.getVoices()` del navegador/sistema; no representa otros paquetes MP3 del sitio. No se generaron nuevas voces ni se capturó TTS.
- Descarga solicitada por el propietario de este proyecto. La consulta no estableció una licencia explícita de redistribución para estos audios; esta documentación registra procedencia, no atribuye una licencia.

## Organización y verificación

`names-es/`, `names-en/` y `verses-es/` contienen los tres conjuntos descargados. `manifest.json` conserva el catálogo fuente, traducciones, dichos, URL de cada archivo, tamaño, SHA-256 y resultados de las rutas no disponibles.

Los números 55–60 son Guacamole, Taco, Chile, Elote, Tuna y Guitarra; se conservan en estos paquetes para reflejar todo lo disponible, sin modificar el catálogo de 54 cartas de la aplicación.

`scripts/verify-loteriacaller.py` verifica los hashes, los números únicos 1–60 por conjunto y la decodificación completa mediante FFmpeg. No equivale a una escucha humana completa. Genera ZIPs en `dist/voice-packs/`; los informes incluidos describen la extracción completa aunque el ZIP contenga un solo conjunto.

Las 54 cartas clásicas de cada paquete se integran en el selector como Generada · Español, Generada · Inglés y Generada · Dichos en español. Las seis cartas modernas permanecen solo en la extracción. No se cambia automáticamente la selección actual.
