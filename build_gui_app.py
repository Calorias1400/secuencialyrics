#!/usr/bin/env python3
"""
Script para construir la aplicación GUI macOS del Generador de Secuencias de Video.
"""

import os
import subprocess
import sys
import shutil


def run_command(command, description):
    """Ejecuta un comando y maneja errores."""
    print(f"🔨 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        print(f"Comando: {command}")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def main():
    print("🎬 Construyendo Generador de Secuencias de Video GUI para macOS")
    print("=" * 65)
    
    # Verificar archivos necesarios
    required_files = ["video_sequence_generator.py", "video_sequence_generator_gui.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Error: No se encuentra {file}")
            print("Asegúrate de tener todos los archivos en el directorio del proyecto.")
            sys.exit(1)
    
    # Limpiar builds anteriores
    print("🧹 Limpiando builds anteriores...")
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Eliminado: {folder}/")
    
    # Verificar/instalar PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        run_command("pip3 install pyinstaller", "Instalación de PyInstaller")
    
    # Construir la aplicación GUI
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",  # Crear un solo archivo ejecutable
        "--windowed",  # Aplicación con ventana (sin consola)
        "--name=GeneradorSecuenciasVideoGUI",
        "--add-data=video_sequence_generator.py:.",  # Incluir módulo principal
        "--add-data=README.md:.",  # Incluir README
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.scrolledtext",
        "video_sequence_generator_gui.py"
    ]
    
    # Si hay icono, agregarlo
    if os.path.exists("app_icon.icns"):
        pyinstaller_cmd.insert(-1, "--icon=app_icon.icns")
    
    run_command(" ".join(pyinstaller_cmd), "Construcción de la aplicación GUI")
    
    # Verificar que se creó la aplicación
    app_path = "dist/GeneradorSecuenciasVideoGUI"
    if os.path.exists(app_path):
        print(f"🎉 ¡Aplicación GUI creada exitosamente!")
        print(f"📍 Ubicación: {os.path.abspath(app_path)}")
        print(f"💾 Tamaño: {os.path.getsize(app_path) / (1024*1024):.1f} MB")
        
        # Hacer ejecutable
        run_command(f"chmod +x '{app_path}'", "Configuración de permisos")
        
        # Crear un .app bundle más amigable para macOS
        app_bundle_path = "dist/GeneradorSecuenciasVideoGUI.app"
        if not os.path.exists(app_bundle_path):
            print("📦 Creando bundle .app para macOS...")
            os.makedirs(f"{app_bundle_path}/Contents/MacOS", exist_ok=True)
            os.makedirs(f"{app_bundle_path}/Contents/Resources", exist_ok=True)
            
            # Mover el ejecutable
            shutil.move(app_path, f"{app_bundle_path}/Contents/MacOS/GeneradorSecuenciasVideoGUI")
            
            # Crear Info.plist
            plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>GeneradorSecuenciasVideoGUI</string>
    <key>CFBundleIdentifier</key>
    <string>com.generador.secuencias.video</string>
    <key>CFBundleName</key>
    <string>Generador Secuencias Video</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.9</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>"""
            
            with open(f"{app_bundle_path}/Contents/Info.plist", "w") as f:
                f.write(plist_content)
            
            print(f"✅ Bundle .app creado: {app_bundle_path}")
        
        print("\n📋 Instrucciones:")
        print(f"1. La aplicación está en: {app_bundle_path}")
        print(f"2. Puedes arrastrarla a /Applications/ para instalarla")
        print(f"3. Haz doble clic para ejecutar la interfaz gráfica")
        print(f"4. Si macOS bloquea la app, ve a: Sistema > Seguridad y Privacidad")
        print(f"5. La aplicación tiene interfaz gráfica intuitiva")
        
    else:
        print("❌ Error: No se pudo crear la aplicación")
        sys.exit(1)


if __name__ == "__main__":
    main()