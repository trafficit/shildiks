import os
import threading
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Preprocess image: crop, grayscale, enhance contrast and sharpness
def preprocess_image(image_path):
    image = Image.open(image_path)
    image = image.convert('L')  # Grayscale

    # Crop borders (keep central area)
    width, height = image.size
    left = int(width * 0.1)
    top = int(height * 0.1)
    right = int(width * 0.9)
    bottom = int(height * 0.9)
    image = image.crop((left, top, right, bottom))

    # Enhance contrast and sharpness
    image = ImageEnhance.Contrast(image).enhance(2.0)
    image = ImageEnhance.Sharpness(image).enhance(2.0)
    image = image.filter(ImageFilter.MedianFilter(size=3))

    return image

# Main processing function
def process_images():
    input_folder = input_path.get()
    output_file = output_path.get()
    format_choice = format_var.get()

    if not os.path.isdir(input_folder):
        messagebox.showerror("Error", "Invalid input folder.")
        return
    if not output_file:
        messagebox.showerror("Error", "Please specify output file.")
        return

    log_text.set("Processing started...")

    results = []

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_path = os.path.join(input_folder, filename)
            try:
                processed_image = preprocess_image(image_path)
                text = pytesseract.image_to_string(
                    processed_image,
                    config='--psm 6 -c tessedit_char_whitelist=0123456789'
                )
                results.append((filename, text.strip()))
            except Exception as e:
                results.append((filename, f"Error: {str(e)}"))

    # Save results
    try:
        if format_choice == "Excel (.xlsx)":
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Shildiki"
            ws.append(["Filename", "Recognized Digits"])
            for filename, text in results:
                ws.append([filename, text])
            wb.save(output_file)
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                for filename, text in results:
                    f.write(f"{filename}: {text}\n")
        log_text.set(f"✅ Done! Saved to {output_file}")
    except Exception as e:
        log_text.set(f"❌ Error saving file: {str(e)}")

# GUI setup
def start_processing():
    threading.Thread(target=process_images).start()

def stop_processing():
    messagebox.showinfo("Info", "Stop button is not implemented yet.")

def browse_input():
    folder = filedialog.askdirectory()
    if folder:
        input_path.set(folder)

def browse_output():
    format_choice = format_var.get()
    ext = ".xlsx" if format_choice == "Excel (.xlsx)" else ".txt"
    filetypes = [("Excel files", "*.xlsx")] if ext == ".xlsx" else [("Text files", "*.txt")]
    file = filedialog.asksaveasfilename(defaultextension=ext, filetypes=filetypes)
    if file:
        output_path.set(file)

# Create window
root = tk.Tk()
root.title("Shildik OCR Dashboard")
root.geometry("600x350")

input_path = tk.StringVar()
output_path = tk.StringVar()
log_text = tk.StringVar()
format_var = tk.StringVar(value="Excel (.xlsx)")

# Input folder
tk.Label(root, text="📂 Input folder with images:").pack(anchor='w', padx=10, pady=5)
tk.Entry(root, textvariable=input_path, width=70).pack(padx=10)
tk.Button(root, text="Browse", command=browse_input).pack(pady=5)

# Format selection
tk.Label(root, text="📋 Select output format:").pack(anchor='w', padx=10, pady=5)
format_menu = ttk.Combobox(root, textvariable=format_var, values=["Excel (.xlsx)", "Text (.txt)"], state="readonly", width=20)
format_menu.pack(padx=10)

# Output file
tk.Label(root, text="📁 Output file path:").pack(anchor='w', padx=10, pady=5)
tk.Entry(root, textvariable=output_path, width=70).pack(padx=10)
tk.Button(root, text="Browse", command=browse_output).pack(pady=5)

# Start/Stop buttons
frame = tk.Frame(root)
frame.pack(pady=10)
tk.Button(frame, text="▶️ Start", command=start_processing, width=15, bg="green", fg="white").pack(side='left', padx=10)
tk.Button(frame, text="⏹ Stop", command=stop_processing, width=15, bg="red", fg="white").pack(side='left', padx=10)

# Log output
tk.Label(root, textvariable=log_text, fg="blue").pack(pady=10)

root.mainloop()
