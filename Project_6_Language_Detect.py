from langdetect import detect
import tkinter as tk
from tkinter import messagebox, ttk

# Language dictionary
lang_dict = {
    'af': 'Afrikaans',
    'ar': 'Arabic',
    'bg': 'Bulgarian',
    'bn': 'Bengali',
    'ca': 'Catalan',
    'cs': 'Czech',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'el': 'Greek',
    'en': 'English',
    'es': 'Spanish',
    'et': 'Estonian',
    'fa': 'Persian',
    'fi': 'Finnish',
    'fr': 'French',
    'gu': 'Gujarati',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hr': 'Croatian',
    'hu': 'Hungarian',
    'id': 'Indonesian',
    'it': 'Italian',
    'ja': 'Japanese',
    'kn': 'Kannada',
    'ko': 'Korean',
    'lt': 'Lithuanian',
    'lv': 'Latvian',
    'mk': 'Macedonian',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'ne': 'Nepali',
    'nl': 'Dutch',
    'no': 'Norwegian',
    'pa': 'Punjabi',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'sq': 'Albanian',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Thai',
    'tl': 'Tagalog',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'vi': 'Vietnamese',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)'
}


def detect_language():
    text = text_entry.get("1.0", tk.END).strip()
    name = name_entry.get().strip()

    if not name:
        messagebox.showwarning("Warning", "Please enter your name")
        return

    if not text:
        messagebox.showwarning("Warning", "Please enter some text to detect")
        return

    try:
        language_code = detect(text)
        language_name = lang_dict.get(language_code, "Unknown Language")
        result_label.config(text=f"Hello {name}! The detected language is: {language_name}")
    except:
        messagebox.showerror("Error", "Could not detect the language. Please try with different text.")


# Create main window
root = tk.Tk()
root.title("Language Detector")
root.geometry("500x400")

# Welcome label
welcome_label = tk.Label(root, text="Welcome to Lets Detect Your Language", font=("Arial", 14, "bold"))
welcome_label.pack(pady=10)

# Separator
ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=5)

# Name entry
name_frame = tk.Frame(root)
name_frame.pack(pady=10)

tk.Label(name_frame, text="What is your name?").pack(side=tk.LEFT)
name_entry = tk.Entry(name_frame, width=30)
name_entry.pack(side=tk.LEFT, padx=10)

# Text entry
text_frame = tk.Frame(root)
text_frame.pack(pady=10)

tk.Label(text_frame, text="Enter text in any language:").pack()
text_entry = tk.Text(text_frame, width=50, height=8)
text_entry.pack()

# Detect button
detect_button = tk.Button(root, text="Detect Language", command=detect_language, bg="#4CAF50", fg="white")
detect_button.pack(pady=15)

# Result label
result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

root.mainloop()
