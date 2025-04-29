from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import ttk, messagebox


def translate_text():
    text = text_entry.get("1.0", "end-1c").strip()
    src_lang = src_lang_var.get().lower()
    dest_lang = dest_lang_var.get().lower()

    if not text:
        messagebox.showwarning("Warning", "Please enter text to translate")
        return

    try:
        translated = GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
        translated_text_entry.delete("1.0", "end")
        translated_text_entry.insert("1.0", translated)
    except Exception as e:
        messagebox.showerror("Error", f"Translation failed: {str(e)}")


# Create main window
root = tk.Tk()
root.title("Language Translator")
root.geometry("600x400")

# Supported languages (using language codes that deep-translator accepts)
LANGUAGES = {
    "Auto": "auto",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh",
    "Japanese": "ja",
    "Hindi": "hi",
    "Arabic": "ar",
    "Russian": "ru",
    "Portuguese": "pt",
    "Italian": "it",
    "Korean": "ko"
}

# Variables for comboboxes
src_lang_var = tk.StringVar()
dest_lang_var = tk.StringVar()

# Source language selection
src_lang_label = ttk.Label(root, text="Source Language:")
src_lang_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

src_lang_combobox = ttk.Combobox(root, textvariable=src_lang_var,
                                 values=list(LANGUAGES.keys()))
src_lang_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
src_lang_combobox.set("English")  # Default value

# Destination language selection
dest_lang_label = ttk.Label(root, text="Target Language:")
dest_lang_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

dest_lang_combobox = ttk.Combobox(root, textvariable=dest_lang_var,
                                  values=list(LANGUAGES.keys()))
dest_lang_combobox.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
dest_lang_combobox.set("Spanish")  # Default value

# Text to translate
text_label = ttk.Label(root, text="Text to Translate:")
text_label.grid(row=2, column=0, padx=10, pady=10, sticky="nw")

text_entry = tk.Text(root, height=5, width=40)
text_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

# Translate button
translate_button = ttk.Button(root, text="Translate", command=translate_text)
translate_button.grid(row=3, column=0, columnspan=2, pady=10)

# Translated text
translated_text_label = ttk.Label(root, text="Translated Text:")
translated_text_label.grid(row=4, column=0, padx=10, pady=10, sticky="nw")

translated_text_entry = tk.Text(root, height=5, width=40)
translated_text_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

# Configure grid weights to make widgets expand with window
root.columnconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(4, weight=1)

root.mainloop()
