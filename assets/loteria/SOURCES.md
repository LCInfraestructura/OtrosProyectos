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

Aplicación interna y no comercial para jugar en una oficina. El propietario del proyecto autorizó expresamente el uso de estas tres fuentes. Consulta realizada el 14 de septiembre de 2026.

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

## Audio principal — pendiente de obtención

- Proyecto: Lotería Mexicana.
- Publicado por Radio Precaución.
- Realizado por alumnos del taller de Radio del Colegio Calmécac de Jalisco, México.
- Fuente: https://www.radioteca.net/audioseries/loteria-mexicana/
- Publicación: 1 de diciembre de 2014.
- Descripción de la fuente: colección sonora de las 54 fichas.
- Licencia: Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional, CC BY-NC-SA 4.0.
- Licencia completa: https://creativecommons.org/licenses/by-nc-sa/4.0/
- Uso del proyecto: interno y no comercial.
- Estado real: conexiones HTTP/HTTPS a la fuente agotaron su tiempo de espera. La página accesible mediante búsqueda únicamente expone cuatro pistas. No se han descargado ni normalizado audios de Radioteca y no se da por completo este conjunto.
- `radioteca-downloads.json` conserva las cuatro direcciones observadas; no se inventaron URLs para las otras 50 pistas. El script de descarga permite completar esa lista con enlaces verificados, sin alterar el catálogo.
- `scripts/process-radioteca.py` está preparado para analizar originales y normalizarlos, pero no se ha ejecutado sobre Radioteca. Conserva originales y escribe archivos derivados en las rutas del catálogo.

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

Los recursos se consumen desde archivos locales. No hay descargas durante una partida ni sustituciones automáticas de conjuntos incompletos. La configuración inicial actual es `pixel + loteriacard` con giro activado; se respetan selecciones guardadas. Radioteca continúa pendiente.
