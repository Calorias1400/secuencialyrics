#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import os, re
from datetime import timedelta
from tkinter import Tk, Label, Entry, Button, filedialog, StringVar, IntVar, messagebox

# ——— Funciones auxiliares ———
def parse_time(time_str):
    h,m,s_ms = time_str.split(":")
    s,ms = s_ms.split(",")
    return timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms))

def time_to_frames(td, fps):
    return int(td.total_seconds() * fps)

def leer_srt(path):
    text = open(path, encoding="utf-8").read()
    blocks = re.findall(r"\d+\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+)", text)
    return [{"inicio": parse_time(s), "fin": parse_time(e), "texto": t} for s,e,t in blocks]

def leer_markers(path):
    tree = ET.parse(path)
    markers = []
    for m in tree.iter('marker'):
        f = int(m.find("start").text)
        # Premiere usa timebase 48000 ticks/sec
        markers.append(timedelta(seconds=f/48000))
    return sorted(markers)

def generar_bloques(subs, markers):
    bloques = []
    for i in range(len(markers)-1):
        ini, fin = markers[i], markers[i+1]
        grupo = [s for s in subs if ini <= s["inicio"] < fin]
        if grupo:
            bloques.append((ini, fin, grupo))
    return bloques

def generar_timeline(bloques, fps):
    imgs = []
    cnt = 1
    for ini, fin, subs in bloques:
        for idx, sub in enumerate(subs):
            start = sub["inicio"]
            # si no es último subtítulo, dura hasta fin de bloque
            end = fin if idx < len(subs)-1 else sub["fin"]
            imgs.append({
                "archivo": f"{cnt}.png",
                "in": time_to_frames(start, fps),
                "out": time_to_frames(end, fps)
            })
            cnt += 1
    return imgs

def exportar_xml(imgs, out, fps):
    root = ET.Element("xmeml", version="5")
    seq = ET.SubElement(root, "sequence"); ET.SubElement(seq, "name").text = "AutoSeq"
    rate = ET.SubElement(seq, "rate")
    ET.SubElement(rate, "timebase").text = str(fps); ET.SubElement(rate, "ntsc").text = "FALSE"
    media = ET.SubElement(seq, "media"); video = ET.SubElement(media, "video")
    track = ET.SubElement(video, "track")
    for i, img in enumerate(imgs):
        clip = ET.SubElement(track, "clipitem", id=f"clip-{i}")
        ET.SubElement(clip, "name").text = img["archivo"]
        ET.SubElement(clip, "start").text = str(img["in"])
        ET.SubElement(clip, "end").text = str(img["out"])
        ET.SubElement(clip, "in").text = "0"
        ET.SubElement(clip, "out").text = str(img["out"]-img["in"])
        f = ET.SubElement(clip, "file", id=f"file-{i}")
        ET.SubElement(f, "name").text = img["archivo"]
        ET.SubElement(f, "pathurl").text = f"file://{img['archivo']}"
    ET.ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)

# ——— GUI con Tkinter ———
class App:
    def __init__(self, root):
        root.title("Auto Premiere Sequence")
        Label(root, text="FPS:").grid(row=0, column=0, padx=4, pady=4)
        self.fps = IntVar(value=24)
        Entry(root, textvariable=self.fps).grid(row=0, column=1)
        Button(root, text="Seleccionar .srt", command=self.sel_srt).grid(row=1, column=0, columnspan=2, sticky="ew", padx=4)
        Button(root, text="Seleccionar XML markers", command=self.sel_xml).grid(row=2, column=0, columnspan=2, sticky="ew", padx=4)
        Button(root, text="Seleccionar carpeta imágenes", command=self.sel_imgs).grid(row=3, column=0, columnspan=2, sticky="ew", padx=4)
        Button(root, text="Generar Secuencia", command=self.run).grid(row=4, column=0, columnspan=2, sticky="ew", padx=4, pady=6)
        self.paths = {"srt": None, "xml": None, "imgs": None}

    def sel_srt(self):
        p = filedialog.askopenfilename(filetypes=[("SRT","*.srt")])
        self.paths["srt"] = p

    def sel_xml(self):
        p = filedialog.askopenfilename(filetypes=[("XML","*.xml")])
        self.paths["xml"] = p

    def sel_imgs(self):
        p = filedialog.askdirectory()
        self.paths["imgs"] = p

    def run(self):
        try:
            fps = self.fps.get()
            subs = leer_srt(self.paths["srt"])
            marks = leer_markers(self.paths["xml"])
            bloques = generar_bloques(subs, marks)
            timeline = generar_timeline(bloques, fps)
            out = "secuencia_generada.xml"
            exportar_xml(timeline, out, fps)
            messagebox.showinfo("Listo", "Importa 'secuencia_generada.xml' en Premiere.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = Tk()
    root.geometry("300x200")
    App(root)
    root.mainloop()