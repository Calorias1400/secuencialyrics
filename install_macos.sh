#!/bin/bash

# Script de instalación automatizada para macOS
# Generador de Secuencias de Video

set -e  # Salir si hay errores

echo "🎬 Instalador del Generador de Secuencias de Video para macOS"
echo "=============================================================="

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script es solo para macOS"
    exit 1
fi

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "💡 Instala Python 3 desde: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Verificar archivos necesarios
required_files=("video_sequence_generator.py" "video_sequence_generator_gui.py" "build_gui_app.py")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Error: No se encuentra $file"
        echo "Asegúrate de ejecutar este script en el directorio del proyecto."
        exit 1
    fi
done

# Instalar PyInstaller si no está instalado
echo "📦 Verificando PyInstaller..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install pyinstaller
else
    echo "✅ PyInstaller ya está instalado"
fi

# Construir la aplicación
echo "🔨 Construyendo aplicación..."
python3 build_gui_app.py

# Verificar que se construyó correctamente
app_path="dist/GeneradorSecuenciasVideoGUI.app"
if [[ ! -d "$app_path" ]]; then
    echo "❌ Error: No se pudo construir la aplicación"
    exit 1
fi

echo "🎉 ¡Aplicación construida exitosamente!"

# Preguntar si instalar en /Applications/
echo ""
read -p "¿Quieres instalar la aplicación en /Applications/? (s/N): " install_choice

if [[ $install_choice =~ ^[Ss]$ ]]; then
    echo "📲 Instalando en /Applications/..."
    
    # Verificar si ya existe y preguntar si reemplazar
    if [[ -d "/Applications/GeneradorSecuenciasVideoGUI.app" ]]; then
        read -p "La aplicación ya existe. ¿Reemplazar? (s/N): " replace_choice
        if [[ $replace_choice =~ ^[Ss]$ ]]; then
            rm -rf "/Applications/GeneradorSecuenciasVideoGUI.app"
        else
            echo "❌ Instalación cancelada"
            exit 1
        fi
    fi
    
    # Copiar la aplicación
    cp -r "$app_path" "/Applications/"
    
    echo "✅ Aplicación instalada en /Applications/"
    echo "🚀 Puedes encontrarla en Launchpad o en la carpeta Aplicaciones"
    
    # Preguntar si abrir
    read -p "¿Quieres abrir la aplicación ahora? (s/N): " open_choice
    if [[ $open_choice =~ ^[Ss]$ ]]; then
        open "/Applications/GeneradorSecuenciasVideoGUI.app"
    fi
else
    echo "📁 La aplicación está disponible en: $PWD/$app_path"
    echo "💡 Puedes arrastrarla a /Applications/ manualmente"
fi

echo ""
echo "📋 Resumen:"
echo "   ✅ Aplicación construida: $app_path"
echo "   🎯 Interfaz gráfica intuitiva"
echo "   🔧 Procesa subtítulos, markers e imágenes"
echo "   📤 Genera XML compatible con editores de video"
echo ""
echo "🔒 Nota sobre permisos:"
echo "   Si macOS bloquea la aplicación al primer uso:"
echo "   1. Ve a Sistema > Seguridad y Privacidad"
echo "   2. Haz clic en 'Abrir de todas formas'"
echo ""
echo "🎬 ¡Disfruta creando secuencias de video automatizadas!"