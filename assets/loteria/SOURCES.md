# Procedencia de los recursos

## Nuevas voces y efecto de giro — LoteriaCard

- Repositorio: https://github.com/jdvilla94/LoteriaCard
- Autor/cuenta del repositorio: jdvilla94.
- Fuente local proporcionada por el usuario: `C:\Users\AnthonyArredondo\Documents\LoteriaCard\LoteriaCard\audioFiles`.
- Se importaron 54 voces MP3 como conjunto `loteriacard` y `flipCard.mp3` como efecto independiente.
- Correspondencia por nombre canónico sin espacios, mayúsculas ni acentos; no por orden del directorio. Se preservan títulos personalizados existentes.
- Sin procesamiento de audio: copia exacta de los originales. `loteriacard-provenance.json` conserva nombres originales y hashes SHA-256. La referencia al repositorio acredita la procedencia, sin atribuir una licencia no verificada.
- Nuevo valor inicial: `pixel + loteriacard`, giro activado. Se respetan preferencias guardadas de partidas anteriores.
- Secuencia: efecto de giro, voz completa, espera configurada. El efecto se puede desactivar. Sin audio silencia efecto y voz.

Aplicación interna y no comercial para jugar en una oficina. El propietario del proyecto autorizó expresamente el uso de las fuentes utilizadas. Consulta realizada el 14 de septiembre de 2026.

## Imágenes tradicionales y audio alternativo

- Proyecto: LoteriaMexicana.
- Autor: fcopaveltorres.
- Fuente: https://github.com/fcopaveltorres/LoteriaMexicana
- Imágenes originales: `cartas/1.jpg` a `cartas/54.jpg`.
- Audio elegido del repositorio: `audio/pavel/1.m4a` a `audio/pavel/54.m4a`.
- El código original `library/script.js` relaciona la imagen y el audio mediante el mismo número. No se usa el orden del directorio. El archivo 0 corresponde al inicio y no es una carta.
- No se incorpora la aplicación original como dependencia.
- Procesamiento: renombrado únicamente; se conservan los bytes originales. El ZIP original queda en `downloads/repo.zip` (no se incluye en el ejecutable).
- `repo-provenance.json` registra ruta original, destino y SHA-256 de cada archivo importado.
- Las 54 imágenes se revisaron en una hoja de contacto. Los 54 audios se decodificaron con FFmpeg; el mapeo se verificó contra el código fuente. Está pendiente la escucha humana completa de las 54 grabaciones.

## Voces generadas — LoteriaCaller

- Fuente: https://www.loteriacaller.com/
- El sitio identifica las grabaciones como pregeneradas con Amazon Polly; no se infiere el nombre del locutor.
- Tres conjuntos: `generated-es` (nombre en español), `generated-en` (nombre en inglés), `generated-verses-es` (dicho en español).
- 54 pistas clásicas por conjunto, vinculadas por número al catálogo fuente. MP3 originales sin modificación de velocidad ni normalización.
- `generated-provenance.json` registra URL original, ID, ruta integrada y SHA-256. Procedencia completa: `../audio-packs/loteriacaller/SOURCES.md`.
- Radioteca se retiró por solicitud del propietario; nunca se obtuvieron sus grabaciones.

## Pixel Art

- Proyecto: Mexican Lotería — Pixel Art Sprite Pack.
- Autor: JoseMariaGarciaMarquez / El Chemas.
- Fuente: https://josemariagarciamarquez.itch.io/sprites-loteria
- Archivo oficial: `mexican-loteria-sprites.zip` (92 199 bytes en la descarga realizada).
- Se descargó mediante el flujo gratuito del autor. No fue necesaria una descarga manual.
- El ZIP sí contiene las 54 cartas canónicas, incluida `laarana.png`, aunque su tabla web no la enumera. El Elote y los reversos adicionales no se incorporan al catálogo de 54 cartas.
- Alias explícito: `elcaso.png` corresponde a la carta 36, El Cazo; se verificó visualmente.
- Procesamiento: renombrado únicamente; sin cambios artísticos, recortes ni reescalado del archivo. WPF utiliza NearestNeighbor para ampliar los sprites.
- `pixel-provenance.json` registra nombre original, destino y SHA-256. ZIP original en `downloads/mexican-loteria-sprites.zip`.
- Las 54 imágenes se decodificaron y se revisaron en una hoja de contacto.

## Verificación y reproducción

`scripts/verify-loteria-assets.py` comprueba IDs 1..54, títulos, rutas locales, tamaño no nulo y decodificación. Para audio, FFmpeg analiza volumen y silencios sin modificar archivos. La decodificación no prueba por sí sola el contenido hablado: no equivale a una revisión humana de las voces.

Los recursos se consumen desde archivos locales. No hay descargas durante una partida ni sustituciones automáticas de conjuntos incompletos. La configuración inicial actual es `pixel + loteriacard` con giro activado; se respetan selecciones guardadas. Las voces generadas se seleccionan de forma independiente a las ilustraciones.
