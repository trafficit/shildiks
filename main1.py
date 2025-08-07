import os
import threading
import configparser
import re
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

CONFIG_FILE = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        input_path.set(config.get("Paths", "input", fallback=""))
        output_path.set(config.get("Paths", "output", fallback=""))

def save_config():
    config = configparser.ConfigParser()
    config["Paths"] = {
        "input": input_path.get(),
        "output": output_path.get()
    }
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

def preprocess_image(image_path):
    image = Image.open(image_path)
    image = image.convert("L")
    w, h = image.size
    image = image.crop((int(w * 0.1), int(h * 0.1), int(w * 0.9), int(h * 0.9)))
    image = ImageEnhance.Contrast(image).enhance(1.5)
    image = ImageEnhance.Sharpness(image).enhance(1.5)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    return image

def clean_shield_line(line):
    if line.startswith("++"):
        cleaned = re.sub(r"[^\w\s.,:;!?()-]", "", line)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        return cleaned if cleaned else " Пустая строка после очистки"
    return line

def process_images():
    folder = input_path.get()
    outfile = output_path.get()
    outformat = format_var.get()

    if not os.path.isdir(folder):
        messagebox.showerror("Error", "Input folder is invalid.")
        return
    if not outfile:
        messagebox.showerror("Error", "Please select an output file.")
        return

    log_text.set("⏳ Processing started...")
    results = []

    for file in os.listdir(folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            try:
                path = os.path.join(folder, file)
                img = preprocess_image(path)
                print(f"\n📄 Processing: {file}")

                raw_text = pytesseract.image_to_string(img, config='--oem 1 --psm 3')
                print(f"🔍 Raw OCR output:\n{raw_text}")
                lines = []
                for line in raw_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("++"):
                        line = clean_shield_line(line)
                    lines.append(line)
                results.append((file, lines if lines else [" No text detected."]))
            except Exception as e:
                print(f"❌ Error with {file}: {str(e)}")
                results.append((file, [f"Error: {str(e)}"]))

    try:
        os.makedirs(os.path.dirname(outfile), exist_ok=True)

        if outformat == "Text (.txt)":
            with open(outfile, "w", encoding="utf-8") as f:
                for file, lines in results:
                    f.write(f"{file}\n")
                    for line in lines:
                        f.write(f"- {line}\n")
                    f.write("\n")

        elif outformat == "PDF (.pdf)":
            c = canvas.Canvas(outfile, pagesize=A4)
            w, h = A4
            y = h - 50
            c.setFont("Helvetica", 12)

            for file, lines in results:
                c.drawString(50, y, f"File: {file}")
                y -= 20
                for line in lines:
                    if y < 50:
                        c.showPage()
                        y = h - 50
                        c.setFont("Helvetica", 12)
                    c.drawString(70, y, f"- {line}")
                    y -= 20
                y -= 30

            c.setFillColorRGB(0.96, 0.49, 0.0)
            c.setFont("Helvetica-Bold", 9)
            c.drawRightString(w - 12, 6, "Created by Alex, 2025 · KUKA")
            c.save()

        elif outformat == "CSV (.csv)":
            with open(outfile, "w", encoding="utf-8") as f:
                f.write("File,Text\n")
                for file, lines in results:
                    for line in lines:
                        f.write(f'"{file}","{line}"\n')

        log_text.set(f"✅ Done! Saved to:\n{outfile}")
        save_config()

    except Exception as e:
        log_text.set(f"❌ Save error: {str(e)}")

def start_processing():
    threading.Thread(target=process_images).start()

def browse_input():
    folder = filedialog.askdirectory()
    if folder:
        input_path.set(folder)
        save_config()

def browse_output():
    ext_map = {
        "Text (.txt)": ".txt",
        "PDF (.pdf)": ".pdf",
        "CSV (.csv)": ".csv"
    }
    ext = ext_map.get(format_var.get(), ".txt")
    file = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[("All files", f"*{ext}")])
    if file:
        output_path.set(file)
        save_config()

root = tk.Tk()
root.title("OCR Dashboard")
root.geometry("600x360")

input_path = tk.StringVar()
output_path = tk.StringVar()
log_text = tk.StringVar()
format_var = tk.StringVar(value="Text (.txt)")

tk.Label(root, text="Input folder with images:").pack(anchor="w", padx=10, pady=5)
tk.Entry(root, textvariable=input_path, width=70).pack(padx=10)
tk.Button(root, text="Browse", command=browse_input).pack(pady=5)

tk.Label(root, text="Choose output format:").pack(anchor="w", padx=10, pady=5)
format_box = ttk.Combobox(
    root,
    textvariable=format_var,
    values=["Text (.txt)", "PDF (.pdf)", "CSV (.csv)"],
    state="readonly",
    width=20
)
format_box.pack(padx=10)
format_box.bind("<<ComboboxSelected>>", lambda e: browse_output())

tk.Label(root, text="Output file path:").pack(anchor="w", padx=10, pady=5)
tk.Entry(root, textvariable=output_path, width=70).pack(padx=10)
tk.Button(root, text="Browse", command=browse_output).pack(pady=5)

tk.Button(root, text="Start", command=start_processing, width=18, bg="green", fg="white").pack(pady=10)
tk.Label(root, textvariable=log_text, fg="blue", wraplength=580, justify="left").pack(pady=(5, 15))

tk.Label(root, text="Created by Alex, 2025 · KUKA", fg="#f57c00", font=("Arial", 9, "bold")).place(
    relx=1.0, rely=1.0, anchor="se", x=-10, y=-6
)

load_config()
root.mainloop()
