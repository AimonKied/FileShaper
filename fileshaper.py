import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from datetime import datetime
import moviepy.editor as mp

def load_language(language="en"):
    try:
        file_path = os.path.join(os.path.dirname(__file__), f"{language}.json")
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Language file '{file_path}' not found. Defaulting to English.")
        default_path = os.path.join(os.path.dirname(__file__), "en.json")
        with open(default_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Failed to decode JSON file. Check file format.")

def choose_folder():
    folder = filedialog.askdirectory()
    folder_path.set(folder)

def get_capture_date(file_path):
    if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        try:
            image = Image.open(file_path)
            exif_data = image._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    if tag in (36867, 36868):
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
        except Exception as e:
            print(f"Fehler beim Lesen der EXIF-Daten: {e}")
    elif file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        try:
            video = mp.VideoFileClip(file_path)
            return datetime.fromtimestamp(os.path.getctime(file_path))
        except Exception as e:
            print(f"Fehler beim Lesen der Videodaten: {e}")
    return None

def get_image_orientation(file_path):
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            return "Hochformat" if height > width else "Querformat"
    except Exception as e:
        print(f"Fehler beim Lesen der Bildgröße: {e}")
        return None

def convert_to_webp(file_path):
    if not os.path.exists(file_path):
        print(f"Datei nicht gefunden: {file_path}")
        return  # Datei existiert nicht, daher Rückkehr
    try:
        with Image.open(file_path) as img:
            webp_path = f"{os.path.splitext(file_path)[0]}.webp"
            img.save(webp_path, "WEBP")
            print(f"Konvertiert: {file_path} -> {webp_path}")
    except Exception as e:
        print(f"Fehler bei der Konvertierung von {file_path} zu WebP: {e}")

def rename_and_sort_files():
    folder = folder_path.get().strip()
    base_name = basename_entry.get().strip()
    file_type = file_type_var.get()
    sort_criteria = sort_criteria_var.get()
    convert_to_webp_option = convert_to_webp_var.get()

    if not os.path.isdir(folder):
        messagebox.showerror(texts["error_invalid_folder"], texts["choose_folder"])
        return
    if not base_name:
        messagebox.showerror(texts["error_enter_base_name"], texts["base_name"])
        return

    supported_formats = {
        texts["images"]: {".jpg", ".jpeg", ".png"},
        texts["videos"]: {".mp4", ".mov", ".avi", ".mkv"}
    }
    
    selected_formats = supported_formats[file_type]
    files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in selected_formats]
    
    if sort_criteria == texts["modification_date"]:
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
    elif sort_criteria == texts["file_name"]:
        files.sort()
    elif sort_criteria == texts["capture_date"] and file_type == texts["images"]:
        files.sort(key=lambda x: get_capture_date(os.path.join(folder, x)) or datetime.min)
    elif sort_criteria == texts["orientation"] and file_type == texts["images"]:
        files.sort(key=lambda x: get_image_orientation(os.path.join(folder, x)) or "")

    for i, file in enumerate(files, start=1):
        old_path = os.path.join(folder, file)
        file_extension = os.path.splitext(file)[1]
        new_name = f"{base_name}{i}{file_extension}"
        new_path = os.path.join(folder, new_name)

        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            # Konvertierung in WebP, wenn die Option ausgewählt ist
            if convert_to_webp_option:
                convert_to_webp(new_path)
        else:
            messagebox.showwarning("Warning", f"{new_name} skipped.")

    messagebox.showinfo(texts["completed"], texts["sort_and_rename"])

def set_language(language):
    global texts
    texts = load_language(language)
    update_texts()

def update_texts():
    label_choose_folder.config(text=texts["choose_folder"])
    label_base_name.config(text=texts["base_name"])
    label_file_type.config(text=texts["file_type"])
    label_sort_by.config(text=texts["sort_by"])
    label_convert_to_webp.config(text=texts["convert_to_webp"])
    sort_button.config(text=texts["sort_and_rename"])
    radio_images.config(text=texts["images"])
    radio_videos.config(text=texts["videos"])
    sort_criteria_dropdown['values'] = (texts["modification_date"], texts["file_name"], texts["capture_date"], texts["orientation"])

root = tk.Tk()
root.title("FileShaper - Dateien Sortierer & Umbenenner")
root.geometry("800x400")
root.minsize(800, 400)
root.configure(bg="#FFFFFF")

texts = load_language("de")

folder_path = tk.StringVar()
basename_entry = tk.StringVar(value="file")
file_type_var = tk.StringVar(value=texts["images"])
sort_criteria_var = tk.StringVar(value=texts["modification_date"])
convert_to_webp_var = tk.BooleanVar(value=False)

language_frame = tk.Frame(root)
language_frame.pack()
tk.Button(language_frame, text="English", command=lambda: set_language("en")).grid(row=0, column=0, padx=5)
tk.Button(language_frame, text="Deutsch", command=lambda: set_language("de")).grid(row=0, column=1, padx=5)

input_frame = ttk.Frame(root, padding="20")
input_frame.pack(pady=20, padx=20, fill='both', expand=True)

label_choose_folder = tk.Label(input_frame, text=texts["choose_folder"], font=('Helvetica', 12))
label_choose_folder.grid(row=0, column=0, padx=10, pady=10, sticky="w")
tk.Entry(input_frame, textvariable=folder_path, width=60).grid(row=0, column=1, padx=10, pady=10)
tk.Button(input_frame, text="Browse", command=choose_folder).grid(row=0, column=2, padx=10, pady=10)

label_base_name = tk.Label(input_frame, text=texts["base_name"], font=('Helvetica', 12))
label_base_name.grid(row=1, column=0, padx=10, pady=10, sticky="w")
tk.Entry(input_frame, textvariable=basename_entry, width=60).grid(row=1, column=1, padx=10, pady=10, columnspan=2)

label_file_type = tk.Label(input_frame, text=texts["file_type"], font=('Helvetica', 12))
label_file_type.grid(row=2, column=0, padx=10, pady=10, sticky="w")
radio_images = tk.Radiobutton(input_frame, text=texts["images"], variable=file_type_var, value=texts["images"], font=('Helvetica', 12))
radio_images.grid(row=2, column=1, padx=10, pady=10, sticky="w")
radio_videos = tk.Radiobutton(input_frame, text=texts["videos"], variable=file_type_var, value=texts["videos"], font=('Helvetica', 12))
radio_videos.grid(row=2, column=2, padx=10, pady=10, sticky="w")

label_sort_by = tk.Label(input_frame, text=texts["sort_by"], font=('Helvetica', 12))
label_sort_by.grid(row=3, column=0, padx=10, pady=10, sticky="w")
sort_criteria_dropdown = ttk.Combobox(input_frame, textvariable=sort_criteria_var, state='readonly')
sort_criteria_dropdown['values'] = (texts["modification_date"], texts["file_name"], texts["capture_date"], texts["orientation"])
sort_criteria_dropdown.grid(row=3, column=1, padx=10, pady=10, columnspan=2)

label_convert_to_webp = tk.Label(input_frame, text=texts["convert_to_webp"], font=('Helvetica', 12))
label_convert_to_webp.grid(row=4, column=0, padx=10, pady=10, sticky="w")
convert_to_webp_checkbox = tk.Checkbutton(input_frame, variable=convert_to_webp_var)
convert_to_webp_checkbox.grid(row=4, column=1, padx=10, pady=10, sticky="w")

sort_button = ttk.Button(root, text=texts["sort_and_rename"], command=rename_and_sort_files)
sort_button.pack(pady=20)

root.mainloop()
