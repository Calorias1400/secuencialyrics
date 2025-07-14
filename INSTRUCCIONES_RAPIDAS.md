# 🚀 Instalación Rápida - macOS

## Opción 1: Instalación Automática (Recomendada)

```bash
./install_macos.sh
```

¡Esto es todo! El script se encarga de:
- ✅ Verificar dependencias
- 📦 Instalar PyInstaller
- 🔨 Construir la aplicación
- 📲 Instalarla en `/Applications/`
- 🚀 Abrirla automáticamente

## Opción 2: Construcción Manual

### Para Interfaz Gráfica:
```bash
python3 build_gui_app.py
```

### Para Línea de Comandos:
```bash
python3 build_app.py
```

## Opción 3: Uso Directo (Sin Construir)

### Con Interfaz Gráfica:
```bash
python3 video_sequence_generator_gui.py
```

### Por Línea de Comandos:
```bash
python3 video_sequence_generator.py
```

---

## 🎯 ¿Cuál Elegir?

| Método | Ventajas | Ideal Para |
|--------|----------|------------|
| **Instalación Automática** | Sin configuración, app nativa de macOS | Usuarios finales |
| **Interfaz Gráfica** | Fácil de usar, selección visual de archivos | Principiantes |
| **Línea de Comandos** | Rápido, scriptable | Usuarios avanzados |

---

## 📁 Archivos Necesarios

Tu proyecto debe tener:
```
├── subtitulos.srt           # Subtítulos de tu video
├── markers_premiere.xml     # Markers exportados de Premiere
└── imagenes/               # Carpeta con imágenes
    ├── 1.png
    ├── 2.png
    └── ...
```

## 📤 Resultado

Se genera `secuencia_generada.xml` que puedes importar en:
- **Final Cut Pro**
- **Adobe Premiere Pro** 
- **DaVinci Resolve**

---

## 🔧 Solución de Problemas

### macOS bloquea la aplicación:
1. **Sistema → Seguridad y Privacidad**
2. Clic en **"Abrir de todas formas"**

### Error de Python:
```bash
# Instalar Python 3
https://www.python.org/downloads/

# Verificar instalación
python3 --version
```

### Permisos de archivos:
```bash
chmod +x install_macos.sh
chmod +x build_gui_app.py
```

---

## 💡 Consejos

- **Usa la instalación automática** para la mejor experiencia
- **La versión GUI** es más fácil para principiantes
- **Arrastra la app** desde `dist/` a `/Applications/` para instalar manualmente
- **Los archivos XML** deben exportarse desde Premiere con markers activos