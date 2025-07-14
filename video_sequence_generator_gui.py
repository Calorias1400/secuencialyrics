#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Secuencias de Video - Versión con Interfaz Gráfica
Script para generar secuencias de video automáticamente a partir de:
- Subtítulos (.srt)
- Markers de Premiere Pro (XML)
- Imágenes numeradas secuencialmente

Genera un XML compatible con Final Cut Pro/Premiere Pro.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from video_sequence_generator import (
    parse_srt_file, parse_premiere_xml, group_subtitles_by_markers,
    calculate_image_clips, generate_fcpxml
)


class VideoSequenceGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Secuencias de Video")
        self.root.geometry("700x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.fps_var = tk.StringVar(value="25")
        self.srt_path_var = tk.StringVar()
        self.xml_path_var = tk.StringVar()
        self.images_folder_var = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        
        # Título
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🎬 Generador de Secuencias de Video",
            font=("Helvetica", 20, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Automatiza la creación de secuencias desde subtítulos y markers",
            font=("Helvetica", 12),
            bg='#f0f0f0',
            fg='#666666'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(padx=30, pady=20, fill='both', expand=True)
        
        # FPS
        fps_frame = tk.LabelFrame(main_frame, text="📊 Configuración", 
                                  font=("Helvetica", 12, "bold"), 
                                  bg='#f0f0f0', fg='#333333')
        fps_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(fps_frame, text="FPS de la secuencia:", 
                bg='#f0f0f0', font=("Helvetica", 10)).pack(anchor='w', padx=10, pady=(10, 5))
        
        fps_entry_frame = tk.Frame(fps_frame, bg='#f0f0f0')
        fps_entry_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        fps_entry = tk.Entry(fps_entry_frame, textvariable=self.fps_var, 
                            font=("Helvetica", 10), width=10)
        fps_entry.pack(side='left')
        
        tk.Label(fps_entry_frame, text="(ej: 24, 25, 30)", 
                bg='#f0f0f0', fg='#666666', font=("Helvetica", 9)).pack(side='left', padx=(10, 0))
        
        # Archivos
        files_frame = tk.LabelFrame(main_frame, text="📁 Archivos de Entrada", 
                                   font=("Helvetica", 12, "bold"), 
                                   bg='#f0f0f0', fg='#333333')
        files_frame.pack(fill='x', pady=(0, 20))
        
        # SRT
        self.create_file_selector(files_frame, "Archivo .srt de subtítulos:", 
                                 self.srt_path_var, self.select_srt_file)
        
        # XML
        self.create_file_selector(files_frame, "XML de Premiere Pro (markers):", 
                                 self.xml_path_var, self.select_xml_file)
        
        # Carpeta de imágenes
        self.create_folder_selector(files_frame, "Carpeta de imágenes numeradas:", 
                                   self.images_folder_var, self.select_images_folder)
        
        # Botón de procesamiento
        process_frame = tk.Frame(main_frame, bg='#f0f0f0')
        process_frame.pack(fill='x', pady=20)
        
        self.process_btn = tk.Button(
            process_frame,
            text="🚀 Generar Secuencia",
            command=self.process_files,
            font=("Helvetica", 14, "bold"),
            bg='#007AFF',
            fg='white',
            relief='flat',
            pady=10,
            cursor='hand2'
        )
        self.process_btn.pack(fill='x')
        
        # Barra de progreso
        self.progress = ttk.Progressbar(process_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=(10, 0))
        self.progress.pack_forget()  # Ocultar inicialmente
        
        # Log de salida
        log_frame = tk.LabelFrame(main_frame, text="📝 Registro de Proceso", 
                                 font=("Helvetica", 12, "bold"), 
                                 bg='#f0f0f0', fg='#333333')
        log_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Monaco", 10),
            bg='#ffffff',
            fg='#333333'
        )
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_file_selector(self, parent, label_text, var, command):
        """Crea un selector de archivo."""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(frame, text=label_text, bg='#f0f0f0', 
                font=("Helvetica", 10)).pack(anchor='w')
        
        entry_frame = tk.Frame(frame, bg='#f0f0f0')
        entry_frame.pack(fill='x', pady=(5, 0))
        
        entry = tk.Entry(entry_frame, textvariable=var, 
                        font=("Helvetica", 9), state='readonly')
        entry.pack(side='left', fill='x', expand=True)
        
        btn = tk.Button(entry_frame, text="Seleccionar", command=command,
                       bg='#34C759', fg='white', relief='flat',
                       font=("Helvetica", 9), cursor='hand2')
        btn.pack(side='right', padx=(10, 0))
        
    def create_folder_selector(self, parent, label_text, var, command):
        """Crea un selector de carpeta."""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(frame, text=label_text, bg='#f0f0f0', 
                font=("Helvetica", 10)).pack(anchor='w')
        
        entry_frame = tk.Frame(frame, bg='#f0f0f0')
        entry_frame.pack(fill='x', pady=(5, 0))
        
        entry = tk.Entry(entry_frame, textvariable=var, 
                        font=("Helvetica", 9), state='readonly')
        entry.pack(side='left', fill='x', expand=True)
        
        btn = tk.Button(entry_frame, text="Seleccionar", command=command,
                       bg='#34C759', fg='white', relief='flat',
                       font=("Helvetica", 9), cursor='hand2')
        btn.pack(side='right', padx=(10, 0))
        
    def select_srt_file(self):
        """Selecciona archivo SRT."""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de subtítulos",
            filetypes=[("Archivos SRT", "*.srt"), ("Todos los archivos", "*.*")]
        )
        if filename:
            self.srt_path_var.set(filename)
            
    def select_xml_file(self):
        """Selecciona archivo XML."""
        filename = filedialog.askopenfilename(
            title="Seleccionar XML de Premiere Pro",
            filetypes=[("Archivos XML", "*.xml"), ("Todos los archivos", "*.*")]
        )
        if filename:
            self.xml_path_var.set(filename)
            
    def select_images_folder(self):
        """Selecciona carpeta de imágenes."""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de imágenes")
        if folder:
            self.images_folder_var.set(folder)
            
    def log(self, message):
        """Añade mensaje al log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def validate_inputs(self):
        """Valida las entradas del usuario."""
        try:
            fps = int(self.fps_var.get())
            if fps <= 0:
                raise ValueError("FPS debe ser positivo")
        except ValueError:
            messagebox.showerror("Error", "FPS debe ser un número entero positivo")
            return False
            
        if not self.srt_path_var.get():
            messagebox.showerror("Error", "Selecciona un archivo .srt")
            return False
            
        if not self.xml_path_var.get():
            messagebox.showerror("Error", "Selecciona un archivo XML de Premiere")
            return False
            
        if not self.images_folder_var.get():
            messagebox.showerror("Error", "Selecciona una carpeta de imágenes")
            return False
            
        # Verificar que la carpeta tiene imágenes numeradas
        images_folder = self.images_folder_var.get()
        has_images = any(f.endswith('.png') and f[:-4].isdigit() 
                        for f in os.listdir(images_folder))
        if not has_images:
            messagebox.showerror("Error", 
                               "La carpeta no contiene imágenes numeradas (1.png, 2.png, etc.)")
            return False
            
        return True
        
    def process_files_thread(self):
        """Procesa los archivos en un hilo separado."""
        try:
            fps = int(self.fps_var.get())
            srt_path = self.srt_path_var.get()
            xml_path = self.xml_path_var.get()
            images_folder = self.images_folder_var.get()
            
            # Parsear archivo SRT
            self.log("🔍 Parseando subtítulos...")
            subtitles = parse_srt_file(srt_path)
            self.log(f"✅ Encontrados {len(subtitles)} subtítulos")
            
            # Parsear XML de Premiere
            self.log("🔍 Parseando markers de Premiere...")
            markers = parse_premiere_xml(xml_path)
            self.log(f"✅ Encontrados {len(markers)} markers")
            
            # Agrupar subtítulos por markers
            self.log("📊 Agrupando subtítulos por markers...")
            subtitle_groups = group_subtitles_by_markers(subtitles, markers)
            self.log(f"✅ Creados {len(subtitle_groups)} grupos de subtítulos")
            
            # Calcular clips de imagen
            self.log("🖼️ Calculando clips de imagen...")
            clips = calculate_image_clips(subtitle_groups, images_folder)
            self.log(f"✅ Generados {len(clips)} clips de imagen")
            
            # Generar XML de salida
            output_path = "secuencia_generada.xml"
            self.log(f"💾 Generando XML de salida: {output_path}")
            generate_fcpxml(clips, fps, output_path)
            
            self.log("🎉 ¡Proceso completado exitosamente!")
            self.log(f"📁 Archivo generado: {os.path.abspath(output_path)}")
            self.log(f"📊 Total de clips: {len(clips)}")
            
            # Mostrar resumen
            if clips:
                self.log("\n=== Resumen de clips ===")
                for i, clip in enumerate(clips[:3]):  # Mostrar solo los primeros 3
                    self.log(f"Clip {i+1}: {os.path.basename(clip.image_path)} "
                            f"({clip.start_time:.2f}s - {clip.end_time:.2f}s)")
                if len(clips) > 3:
                    self.log(f"... y {len(clips) - 3} clips más.")
                    
            # Preguntar si abrir la carpeta
            self.root.after(0, lambda: self.show_completion_dialog(output_path))
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error durante el procesamiento:\n{str(e)}"))
        finally:
            # Ocultar progreso y habilitar botón
            self.root.after(0, self.finish_processing)
            
    def show_completion_dialog(self, output_path):
        """Muestra diálogo de finalización."""
        result = messagebox.askyesno(
            "Proceso Completado",
            f"¡Secuencia generada exitosamente!\n\n"
            f"Archivo: {os.path.basename(output_path)}\n\n"
            f"¿Quieres abrir la carpeta que contiene el archivo?"
        )
        
        if result:
            # Abrir carpeta en Finder (macOS)
            os.system(f"open -R '{os.path.abspath(output_path)}'")
            
    def finish_processing(self):
        """Finaliza el procesamiento."""
        self.progress.pack_forget()
        self.process_btn.config(state='normal', text="🚀 Generar Secuencia")
        
    def process_files(self):
        """Inicia el procesamiento de archivos."""
        if not self.validate_inputs():
            return
            
        # Limpiar log
        self.log_text.delete(1.0, tk.END)
        
        # Mostrar progreso
        self.progress.pack(fill='x', pady=(10, 0))
        self.progress.start()
        self.process_btn.config(state='disabled', text="Procesando...")
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.process_files_thread)
        thread.daemon = True
        thread.start()


def main():
    """Función principal de la GUI."""
    # Verificar si estamos en un bundle de PyInstaller
    if getattr(sys, 'frozen', False):
        # Estamos en un ejecutable de PyInstaller
        application_path = sys._MEIPASS
    else:
        # Estamos ejecutando desde el script
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    root = tk.Tk()
    
    # Configurar icono si existe
    try:
        if sys.platform == 'darwin':  # macOS
            root.iconbitmap('')  # Usar icono por defecto en macOS
    except:
        pass
    
    app = VideoSequenceGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()