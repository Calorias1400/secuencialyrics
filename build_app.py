#!/usr/bin/env python3
"""
Script para construir la aplicación macOS del Generador de Secuencias de Video.
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
    print("🎬 Construyendo Generador de Secuencias de Video para macOS")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("video_sequence_generator.py"):
        print("❌ Error: No se encuentra video_sequence_generator.py")
        print("Asegúrate de ejecutar este script en el directorio del proyecto.")
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
    
    # Construir la aplicación
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",  # Crear un solo archivo ejecutable
        "--windowed",  # No mostrar consola en GUI (comentar si quieres ver la consola)
        "--name=GeneradorSecuenciasVideo",
        "--icon=app_icon.icns",  # Opcional: icono de la app
        "--add-data=README.md:.",  # Incluir README
        "video_sequence_generator.py"
    ]
    
    # Si no hay icono, remover esa opción
    if not os.path.exists("app_icon.icns"):
        pyinstaller_cmd = [cmd for cmd in pyinstaller_cmd if not cmd.startswith("--icon")]
    
    run_command(" ".join(pyinstaller_cmd), "Construcción de la aplicación")
    
    # Verificar que se creó la aplicación
    app_path = "dist/GeneradorSecuenciasVideo"
    if os.path.exists(app_path):
        print(f"🎉 ¡Aplicación creada exitosamente!")
        print(f"📍 Ubicación: {os.path.abspath(app_path)}")
        print(f"💾 Tamaño: {os.path.getsize(app_path) / (1024*1024):.1f} MB")
        
        # Hacer ejecutable
        run_command(f"chmod +x '{app_path}'", "Configuración de permisos")
        
        print("\n📋 Instrucciones:")
        print(f"1. La aplicación está en: dist/GeneradorSecuenciasVideo")
        print(f"2. Puedes moverla a /Applications/ para acceso fácil")
        print(f"3. Al ejecutarla por primera vez, macOS puede pedir permisos")
        print(f"4. Si hay problemas de seguridad, ve a: Sistema > Seguridad y Privacidad")
        
    else:
        print("❌ Error: No se pudo crear la aplicación")
        sys.exit(1)


if __name__ == "__main__":
    main()