# Lotería de escritorio

## Repositorio

Repositorio del proyecto: https://github.com/LCInfraestructura/OtrosProyectos. Rama de trabajo y entrega: `main`.

Las siguientes actualizaciones del programa, audios y otros recursos se versionan y suben a `main`, según lo acordado con el propietario. Se incluyen código, pruebas, catálogo, recursos locales y documentación de procedencia. `dist/`, `downloads/`, `artifacts/` y las salidas de compilación permanecen fuera de Git; los ejecutables portátiles se regeneran con los scripts de publicación y empaquetado.

## Actualización: nuevas voces y giro

Se añadieron las 54 voces de `jdvilla94/LoteriaCard` y su efecto `flipCard.mp3`, suministrados localmente. Selecciona **audio `loteriacard`** y activa **Sonido de giro**. Es el valor inicial en configuraciones nuevas; si ya habías jugado, se conserva tu selección anterior.

La secuencia con el efecto activado es **giro → voz completa → espera configurable**. Pausar y Siguiente controlan también el efecto, sin superponer grabaciones. Sin audio silencia ambos. El efecto se puede usar con cualquiera de las voces.

Importación reproducible: `python scripts/import-loteriacard.py RUTA_DE_AUDIOFILES`. Conserva títulos y registra hashes; no modifica los archivos originales. Procedencia: https://github.com/jdvilla94/LoteriaCard.

Aplicación nativa WPF para Windows 11, sin cuentas, sin suscripción y sin internet durante el juego.

## Pantalla de juego y configuración

La pantalla principal muestra la carta, el historial y los controles de partida. **Configuración**, en la esquina superior derecha, abre una ventana independiente para ajustar ritmo, ilustraciones, voz, giro y volumen. No hay opciones de configuración ocupando espacio en la mesa.

**Guardar y cerrar** conserva los ajustes inmediatamente. **Cancelar** o cerrar con la X descarta los cambios de esa ventana. Abrir configuración durante una partida la pausa; para cambiar las opciones de esa ronda hay que iniciar una nueva partida. Al cerrar, pulsa Continuar cuando la mesa esté lista.

El diseño usa tonos crema, verde suave y terracota, controles redondeados y títulos más grandes. La distribución se adapta desde 950 × 650 hasta pantalla completa.

## Abrir

Abre `dist/Loteria/Loteria.exe`. Conserva su carpeta completa, incluidos `assets` y los archivos de .NET. No requiere instalación.

Están listas las 54 imágenes Pixel Art, las 54 tradicionales, las 54 voces `repo`, las 54 voces `loteriacard` y el efecto de giro. **Selecciona audio `loteriacard` para usar las nuevas voces.** Radioteca sigue pendiente y no se reemplaza automáticamente.

## Jugar

1. Selecciona imágenes y audio. La combinación inicial es `pixel + loteriacard`, con giro activado.
2. Escribe la espera **después del audio**, entre 0.1 y 600 segundos (3 por defecto).
3. Pulsa Iniciar. La primera carta aparece de inmediato.
4. Se reproduce el giro si está activado, luego toda la grabación, después la espera y aparece la siguiente carta.
5. Pausar congela la grabación o el tiempo restante. Continuar retoma desde ese punto.
6. Siguiente permite avanzar manualmente y detiene el audio anterior. Si estabas en pausa, la partida sigue pausada y el nuevo audio se reproduce al continuar.
7. Nueva partida pide confirmación si la partida no ha terminado; borra el historial y prepara una nueva mezcla.

Sin audio se aplica únicamente la espera. Ninguna carta se repite. El historial muestra miniaturas con el mismo título de la carta principal, con la más reciente primero. F11 alterna pantalla completa y Esc sale de ella. Se proyecta la misma ventana.

Las opciones de recursos y tiempo se fijan durante la partida. Para cambiarlas, inicia una nueva partida. Las preferencias se guardan en `%LOCALAPPDATA%/LoteriaOficina/settings.json`.

## Títulos editables en archivo

Edita `assets/loteria/manifest.json` **dentro de la carpeta del ejecutable** y vuelve a abrir la app. Cada carta tiene `id`, `number`, `name`, `title`, `slug`, `images` y `audio`. Cambia únicamente `title` para modificar el texto visible en pantalla e historial; no necesitas renombrar imágenes ni audios.

El catálogo de desarrollo está en `assets/loteria/manifest.json` en la raíz del proyecto. Una nueva publicación copia ese catálogo a la carpeta de distribución: guarda allí también los títulos que quieras conservar entre compilaciones.

Las ilustraciones conservan el texto que forma parte de la imagen original; `title` modifica la etiqueta de la interfaz, no los píxeles del dibujo.

## Desarrollo y pruebas

Requiere .NET SDK 10 para compilar, no para abrir la distribución autónoma.

```powershell
dotnet build src/Loteria
dotnet run --project tests/Loteria.Tests.csproj
powershell -File scripts/publish.ps1
```

Las pruebas recorren 100 mezclas, IDs inválidos, títulos personalizados en ambas vistas, pausa y continuación, historial, fin y reinicio de partida y reproducción WPF real a volumen cero con espera posterior. Generan `artifacts/app-preview.png` para revisar la interfaz. No son una prueba de la salida acústica de los altavoces ni de la televisión.

## Recursos y verificación

Procedencia y estado detallados: `assets/loteria/SOURCES.md`.

Los scripts Python requieren Python 3, Pillow e imageio-ffmpeg. Se puede instalar imageio-ffmpeg en `downloads/python-tools` con `python -m pip install --target downloads/python-tools imageio-ffmpeg`.

```powershell
python scripts/verify-loteria-assets.py
python scripts/verify-loteria-assets.py --available-only
```

La primera comprobación falla mientras falten las 54 pistas de Radioteca. `--available-only` verifica los 217 recursos disponibles, pero sigue mostrando todos los faltantes; no significa que Radioteca esté completo. Reporte en `artifacts/asset-report.json`, con análisis de volumen/silencios y hojas de contacto.

Para reproducir la importación, descarga el ZIP del repositorio en `downloads/repo.zip`, ejecuta `scripts/import-repo.py`, y usa `scripts/download-pixel.py` y `scripts/import-pixel.py` para el pack del autor. Los scripts de importación mantienen las imágenes sin alteraciones artísticas.

## Pendiente: Radioteca

La fuente no respondió a las conexiones de descarga de este equipo. La página consultable muestra cuatro enlaces de audio, aunque describe 54 fichas. `radioteca-downloads.json` solo contiene enlaces efectivamente observados. Necesitamos recuperar las 54 pistas originales o un enlace completo disponible de esa misma fuente para cerrar esta parte.

`scripts/download-radioteca.py` permite reintentar enlaces verificados y conserva originales. `scripts/process-radioteca.py` analiza un conjunto completo y, con `--normalize`, realiza normalización de volumen en dos pasadas a -18 LUFS, pico máximo -1.5 dBTP, sin recortar silencios automáticamente. Este procesamiento todavía no se ha realizado sobre Radioteca y deberá revisarse antes de dar el conjunto por validado.
