# Generador de Secuencias de Video

Script automatizado en Python para generar secuencias de video a partir de subtítulos, markers de Premiere Pro e imágenes numeradas.

## Uso

```bash
python3 video_sequence_generator.py
```

El script te pedirá por consola:

1. **FPS de la secuencia** (ej: 24, 25, 30)
2. **Ruta del archivo .srt** de subtítulos
3. **Ruta del archivo XML** exportado desde Premiere Pro con markers
4. **Ruta de la carpeta** con imágenes numeradas secuencialmente (`1.png`, `2.png`, etc.)

## Funcionamiento

1. **Parsea los subtítulos** del archivo .srt extrayendo tiempos de inicio y fin
2. **Extrae los markers** del XML de Premiere Pro y los ordena cronológicamente
3. **Agrupa los subtítulos** en bloques entre cada par de markers consecutivos
4. **Asigna imágenes** a cada subtítulo siguiendo estas reglas:
   - **Primera imagen del bloque**: desde inicio del bloque hasta fin del último subtítulo
   - **Imágenes intermedias**: desde su subtítulo hasta fin del bloque
   - **Última imagen**: solo la duración de su propio subtítulo
5. **Calcula fotogramas** usando el FPS especificado
6. **Genera un XML** compatible con Final Cut Pro/Premiere Pro

## Salida

El script genera un archivo `secuencia_generada.xml` que puedes importar en tu editor de video preferido.

## Requisitos

- Python 3.6+
- Solo usa librerías estándar (sin dependencias externas)

## Estructura de archivos esperada

```
proyecto/
├── subtitulos.srt
├── markers_premiere.xml
├── imagenes/
│   ├── 1.png
│   ├── 2.png
│   ├── 3.png
│   └── ...
└── secuencia_generada.xml (salida)
```