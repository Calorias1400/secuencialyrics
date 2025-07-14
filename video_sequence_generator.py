#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar secuencias de video automáticamente a partir de:
- Subtítulos (.srt)
- Markers de Premiere Pro (XML)
- Imágenes numeradas secuencialmente

Genera un XML compatible con Final Cut Pro/Premiere Pro.
"""

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any


class SubtitleEntry:
    """Representa una entrada de subtítulo con sus tiempos."""
    
    def __init__(self, index: int, start_time: float, end_time: float, text: str):
        self.index = index
        self.start_time = start_time  # En segundos
        self.end_time = end_time      # En segundos
        self.text = text.strip()


class MarkerEntry:
    """Representa un marker con su tiempo."""
    
    def __init__(self, time: float, name: str = ""):
        self.time = time  # En segundos
        self.name = name


class ImageClip:
    """Representa un clip de imagen con sus tiempos calculados."""
    
    def __init__(self, image_path: str, start_time: float, end_time: float):
        self.image_path = image_path
        self.start_time = start_time  # En segundos
        self.end_time = end_time      # En segundos


def parse_srt_time(time_str: str) -> float:
    """
    Convierte un timestamp SRT (HH:MM:SS,mmm) a segundos.
    
    Args:
        time_str: String en formato "HH:MM:SS,mmm"
    
    Returns:
        float: Tiempo en segundos
    """
    # Reemplazar coma por punto para los milisegundos
    time_str = time_str.replace(',', '.')
    
    # Parsear el tiempo
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    
    return hours * 3600 + minutes * 60 + seconds


def parse_srt_file(srt_path: str) -> List[SubtitleEntry]:
    """
    Parsea un archivo SRT y devuelve una lista de entradas de subtítulos.
    
    Args:
        srt_path: Ruta al archivo .srt
    
    Returns:
        List[SubtitleEntry]: Lista de subtítulos parseados
    """
    subtitles = []
    
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir por bloques de subtítulos (separados por líneas vacías)
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        # Primera línea: índice
        try:
            index = int(lines[0])
        except ValueError:
            continue
        
        # Segunda línea: timestamps
        time_line = lines[1]
        time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', time_line)
        
        if not time_match:
            continue
        
        start_time = parse_srt_time(time_match.group(1))
        end_time = parse_srt_time(time_match.group(2))
        
        # Resto de líneas: texto del subtítulo
        text = '\n'.join(lines[2:])
        
        subtitles.append(SubtitleEntry(index, start_time, end_time, text))
    
    return subtitles


def parse_premiere_xml(xml_path: str) -> List[MarkerEntry]:
    """
    Parsea un archivo XML de Premiere Pro y extrae los markers.
    
    Args:
        xml_path: Ruta al archivo XML de Premiere
    
    Returns:
        List[MarkerEntry]: Lista de markers ordenados cronológicamente
    """
    markers = []
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Buscar markers en diferentes posibles ubicaciones del XML
        # Los markers pueden estar en diferentes estructuras según la versión de Premiere
        marker_elements = []
        
        # Buscar en toda la estructura XML
        for elem in root.iter():
            if 'marker' in elem.tag.lower() or elem.tag.lower() == 'marker':
                marker_elements.append(elem)
        
        for marker in marker_elements:
            # Intentar extraer el tiempo del marker
            time_value = None
            name_value = ""
            
            # Buscar atributos comunes para tiempo
            for attr_name in ['time', 'start', 'timecode', 'in']:
                if attr_name in marker.attrib:
                    time_str = marker.attrib[attr_name]
                    try:
                        # Intentar diferentes formatos de tiempo
                        if ':' in time_str:
                            time_value = parse_srt_time(time_str.replace('.', ','))
                        else:
                            time_value = float(time_str)
                        break
                    except:
                        continue
            
            # Buscar nombre del marker
            for attr_name in ['name', 'comment', 'label']:
                if attr_name in marker.attrib:
                    name_value = marker.attrib[attr_name]
                    break
            
            # Si encontramos texto dentro del elemento
            if marker.text and marker.text.strip():
                name_value = marker.text.strip()
            
            if time_value is not None:
                markers.append(MarkerEntry(time_value, name_value))
    
    except Exception as e:
        print(f"Advertencia: Error al parsear XML de Premiere: {e}")
        print("Continuando sin markers...")
    
    # Ordenar markers cronológicamente
    markers.sort(key=lambda m: m.time)
    
    return markers


def group_subtitles_by_markers(subtitles: List[SubtitleEntry], markers: List[MarkerEntry]) -> List[List[SubtitleEntry]]:
    """
    Agrupa los subtítulos en bloques entre cada par de markers consecutivos.
    
    Args:
        subtitles: Lista de subtítulos
        markers: Lista de markers ordenados cronológicamente
    
    Returns:
        List[List[SubtitleEntry]]: Lista de grupos de subtítulos
    """
    if not markers:
        # Si no hay markers, todos los subtítulos van en un solo grupo
        return [subtitles]
    
    groups = []
    
    for i in range(len(markers)):
        # Determinar el rango de tiempo para este grupo
        start_time = markers[i].time
        end_time = markers[i + 1].time if i + 1 < len(markers) else float('inf')
        
        # Encontrar subtítulos que están en este rango
        group_subtitles = []
        for subtitle in subtitles:
            if start_time <= subtitle.start_time < end_time:
                group_subtitles.append(subtitle)
        
        if group_subtitles:
            groups.append(group_subtitles)
    
    return groups


def calculate_image_clips(subtitle_groups: List[List[SubtitleEntry]], images_folder: str) -> List[ImageClip]:
    """
    Calcula los clips de imagen según las reglas especificadas.
    
    Args:
        subtitle_groups: Grupos de subtítulos
        images_folder: Carpeta con las imágenes numeradas
    
    Returns:
        List[ImageClip]: Lista de clips de imagen calculados
    """
    clips = []
    image_counter = 1
    
    for group in subtitle_groups:
        if not group:
            continue
        
        # Obtener tiempo de inicio del bloque y fin del último subtítulo
        block_start = group[0].start_time
        block_end = max(sub.end_time for sub in group)
        
        for i, subtitle in enumerate(group):
            image_path = os.path.join(images_folder, f"{image_counter}.png")
            
            if i == 0:
                # Primera imagen: desde inicio del bloque hasta fin del último subtítulo del bloque
                start_time = block_start
                end_time = block_end
            elif i == len(group) - 1:
                # Última imagen: solo la duración de su propio subtítulo
                start_time = subtitle.start_time
                end_time = subtitle.end_time
            else:
                # Imágenes intermedias: desde su subtítulo hasta fin del bloque
                start_time = subtitle.start_time
                end_time = block_end
            
            clips.append(ImageClip(image_path, start_time, end_time))
            image_counter += 1
    
    return clips


def seconds_to_frames(seconds: float, fps: int) -> int:
    """Convierte segundos a fotogramas."""
    return int(seconds * fps)


def generate_fcpxml(clips: List[ImageClip], fps: int, output_path: str):
    """
    Genera un archivo XML compatible con Final Cut Pro/Premiere.
    
    Args:
        clips: Lista de clips de imagen
        fps: Frames por segundo
        output_path: Ruta de salida del archivo XML
    """
    # Crear la estructura básica del XML
    root = ET.Element("xmeml", version="1")
    
    # Crear secuencia
    sequence = ET.SubElement(root, "sequence")
    sequence_name = ET.SubElement(sequence, "name")
    sequence_name.text = "Secuencia Generada"
    
    # Configuración de la secuencia
    settings = ET.SubElement(sequence, "settings")
    
    # Video settings
    video_settings = ET.SubElement(settings, "video")
    format_elem = ET.SubElement(video_settings, "format")
    
    samplecharacteristics = ET.SubElement(format_elem, "samplecharacteristics")
    rate = ET.SubElement(samplecharacteristics, "rate")
    timebase = ET.SubElement(rate, "timebase")
    timebase.text = str(fps)
    ntsc = ET.SubElement(rate, "ntsc")
    ntsc.text = "FALSE"
    
    width = ET.SubElement(samplecharacteristics, "width")
    width.text = "1920"
    height = ET.SubElement(samplecharacteristics, "height")
    height.text = "1080"
    
    # Media
    media = ET.SubElement(sequence, "media")
    video_media = ET.SubElement(media, "video")
    track = ET.SubElement(video_media, "track")
    
    # Añadir clips
    for i, clip in enumerate(clips):
        clipitem = ET.SubElement(track, "clipitem", id=f"clipitem-{i+1}")
        
        # Nombre del clip
        name = ET.SubElement(clipitem, "name")
        name.text = os.path.basename(clip.image_path)
        
        # Duración en frames
        duration_frames = seconds_to_frames(clip.end_time - clip.start_time, fps)
        start_frames = seconds_to_frames(clip.start_time, fps)
        end_frames = seconds_to_frames(clip.end_time, fps)
        
        # Tiempos
        start_elem = ET.SubElement(clipitem, "start")
        start_elem.text = str(start_frames)
        
        end_elem = ET.SubElement(clipitem, "end")
        end_elem.text = str(end_frames)
        
        in_elem = ET.SubElement(clipitem, "in")
        in_elem.text = "0"
        
        out_elem = ET.SubElement(clipitem, "out")
        out_elem.text = str(duration_frames)
        
        # Archivo
        file_elem = ET.SubElement(clipitem, "file", id=f"file-{i+1}")
        pathurl = ET.SubElement(file_elem, "pathurl")
        pathurl.text = f"file://{os.path.basename(clip.image_path)}"
        
        # Características del archivo
        media_elem = ET.SubElement(file_elem, "media")
        video_elem = ET.SubElement(media_elem, "video")
        samplecharacteristics_file = ET.SubElement(video_elem, "samplecharacteristics")
        
        rate_file = ET.SubElement(samplecharacteristics_file, "rate")
        timebase_file = ET.SubElement(rate_file, "timebase")
        timebase_file.text = str(fps)
        ntsc_file = ET.SubElement(rate_file, "ntsc")
        ntsc_file.text = "FALSE"
        
        width_file = ET.SubElement(samplecharacteristics_file, "width")
        width_file.text = "1920"
        height_file = ET.SubElement(samplecharacteristics_file, "height")
        height_file.text = "1080"
    
    # Escribir el archivo XML
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def get_user_input():
    """
    Obtiene la información necesaria del usuario por consola.
    
    Returns:
        Tuple: (fps, srt_path, xml_path, images_folder)
    """
    print("=== Generador de Secuencias de Video ===\n")
    
    # FPS
    while True:
        try:
            fps = int(input("Ingresa los FPS de la secuencia (ej: 24, 25, 30): "))
            if fps > 0:
                break
            else:
                print("Por favor, ingresa un número positivo.")
        except ValueError:
            print("Por favor, ingresa un número válido.")
    
    # Archivo SRT
    while True:
        srt_path = input("Ruta del archivo .srt de subtítulos: ").strip()
        if os.path.exists(srt_path) and srt_path.lower().endswith('.srt'):
            break
        else:
            print("Archivo no encontrado o no es un .srt. Intenta de nuevo.")
    
    # Archivo XML de Premiere
    while True:
        xml_path = input("Ruta del archivo XML de Premiere Pro: ").strip()
        if os.path.exists(xml_path) and xml_path.lower().endswith('.xml'):
            break
        else:
            print("Archivo no encontrado o no es un .xml. Intenta de nuevo.")
    
    # Carpeta de imágenes
    while True:
        images_folder = input("Ruta de la carpeta con imágenes numeradas: ").strip()
        if os.path.isdir(images_folder):
            # Verificar que hay al menos una imagen numerada
            has_images = any(f.endswith('.png') and f[:-4].isdigit() 
                           for f in os.listdir(images_folder))
            if has_images:
                break
            else:
                print("La carpeta no contiene imágenes numeradas (1.png, 2.png, etc.).")
        else:
            print("Carpeta no encontrada. Intenta de nuevo.")
    
    return fps, srt_path, xml_path, images_folder


def main():
    """Función principal del script."""
    try:
        # Obtener datos del usuario
        fps, srt_path, xml_path, images_folder = get_user_input()
        
        print("\n=== Procesando archivos ===")
        
        # Parsear archivo SRT
        print("Parseando subtítulos...")
        subtitles = parse_srt_file(srt_path)
        print(f"Encontrados {len(subtitles)} subtítulos.")
        
        # Parsear XML de Premiere
        print("Parseando markers de Premiere...")
        markers = parse_premiere_xml(xml_path)
        print(f"Encontrados {len(markers)} markers.")
        
        # Agrupar subtítulos por markers
        print("Agrupando subtítulos por markers...")
        subtitle_groups = group_subtitles_by_markers(subtitles, markers)
        print(f"Creados {len(subtitle_groups)} grupos de subtítulos.")
        
        # Calcular clips de imagen
        print("Calculando clips de imagen...")
        clips = calculate_image_clips(subtitle_groups, images_folder)
        print(f"Generados {len(clips)} clips de imagen.")
        
        # Generar XML de salida
        output_path = "secuencia_generada.xml"
        print(f"Generando XML de salida: {output_path}")
        generate_fcpxml(clips, fps, output_path)
        
        print(f"\n¡Proceso completado exitosamente!")
        print(f"Archivo generado: {output_path}")
        print(f"Total de clips: {len(clips)}")
        
        # Mostrar resumen de clips
        if clips:
            print("\n=== Resumen de clips ===")
            for i, clip in enumerate(clips[:5]):  # Mostrar solo los primeros 5
                print(f"Clip {i+1}: {os.path.basename(clip.image_path)} "
                      f"({clip.start_time:.2f}s - {clip.end_time:.2f}s)")
            if len(clips) > 5:
                print(f"... y {len(clips) - 5} clips más.")
    
    except KeyboardInterrupt:
        print("\nProceso cancelado por el usuario.")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()