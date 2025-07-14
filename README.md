# Generador de Secuencias de Video

Script automatizado en Python para generar secuencias de video a partir de subtítulos, markers de Premiere Pro e imágenes numeradas.

## 🚀 Aplicación para macOS

### Construcción Rápida (Interfaz Gráfica)
```bash
python3 build_gui_app.py
```

Esto creará una aplicación `GeneradorSecuenciasVideoGUI.app` que puedes:
- **Arrastrar a `/Applications/`** para instalación permanente
- **Ejecutar con doble clic** para abrir la interfaz gráfica
- **Distribuir a otros Macs** sin necesidad de Python

### Construcción Alternativa (Línea de Comandos)
```bash
python3 build_app.py
```

## 💻 Uso desde Python

### Versión con Interfaz Gráfica
```bash
python3 video_sequence_generator_gui.py
```

### Versión de Línea de Comandos
```bash
python3 video_sequence_generator.py
```

## 📋 Configuración

El script te pedirá:

1. **FPS de la secuencia** (ej: 24, 25, 30)
2. **Ruta del archivo .srt** de subtítulos
3. **Ruta del archivo XML** exportado desde Premiere Pro con markers
4. **Ruta de la carpeta** con imágenes numeradas secuencialmente (`1.png`, `2.png`, etc.)

## ⚙️ Funcionamiento

1. **Parsea los subtítulos** del archivo .srt extrayendo tiempos de inicio y fin
2. **Extrae los markers** del XML de Premiere Pro y los ordena cronológicamente
3. **Agrupa los subtítulos** en bloques entre cada par de markers consecutivos
4. **Asigna imágenes** a cada subtítulo siguiendo estas reglas:
   - **Primera imagen del bloque**: desde inicio del bloque hasta fin del último subtítulo
   - **Imágenes intermedias**: desde su subtítulo hasta fin del bloque
   - **Última imagen**: solo la duración de su propio subtítulo
5. **Calcula fotogramas** usando el FPS especificado
6. **Genera un XML** compatible con Final Cut Pro/Premiere Pro

## 📦 Salida

El script genera un archivo `secuencia_generada.xml` que puedes importar directamente en:
- **Final Cut Pro**
- **Adobe Premiere Pro**
- **DaVinci Resolve**

## 🔧 Requisitos

- **Python 3.6+**
- **PyInstaller** (para construcción de apps)
- Solo usa librerías estándar para el procesamiento

## 📁 Estructura de archivos esperada

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

## 🍎 Instalación en macOS

1. **Construye la aplicación:**
   ```bash
   python3 build_gui_app.py
   ```

2. **Instala la app:**
   ```bash
   cp -r dist/GeneradorSecuenciasVideoGUI.app /Applications/
   ```

3. **Ejecuta desde Launchpad o Aplicaciones**

## 🔒 Permisos de macOS

Si macOS bloquea la aplicación:
1. Ve a **Sistema > Seguridad y Privacidad**
2. En la pestaña **General**, haz clic en **"Abrir de todas formas"**
3. O ejecuta: `sudo spctl --master-disable` (temporalmente)