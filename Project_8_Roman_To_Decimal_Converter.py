import tkinter as tk
from tkinter import messagebox

# Dictionary for Roman to Decimal values
t = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}


def romantodecimal(num):
    sum = 0
    for i in range(len(num) - 1):
        left = num[i]
        right = num[i + 1]
        if t[left] < t[right]:
            sum -= t[left]
        else:
            sum += t[left]
    sum += t[num[-1]]
    return sum


def convert():
    roman_num = entry.get().strip().upper()

    # Validate input
    if not roman_num:
        messagebox.showerror("Error", "Please enter a Roman numeral")
        return

    valid_chars = {'I', 'V', 'X', 'L', 'C', 'D', 'M'}
    for char in roman_num:
        if char not in valid_chars:
            messagebox.showerror("Error", f"Invalid Roman numeral character: {char}")
            return

    try:
        decimal_num = romantodecimal(roman_num)
        result_label.config(text=f"The Decimal Number of {roman_num} is {decimal_num}")
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed: {str(e)}")


# Create main window
root = tk.Tk()
root.title("Roman to Decimal Converter")

# Welcome message
welcome_label = tk.Label(root, text="Welcome to Roman to Decimal Converter", font=('Arial', 14))
welcome_label.pack(pady=10)

# Instructions
instructions = tk.Label(root, text="Enter a Roman numeral (I, V, X, L, C, D, M):")
instructions.pack(pady=5)

# Entry widget for Roman numeral
entry = tk.Entry(root, font=('Arial', 12), width=20)
entry.pack(pady=10)

# Convert button
convert_btn = tk.Button(root, text="Convert", command=convert, bg='lightblue')
convert_btn.pack(pady=5)

# Result label
result_label = tk.Label(root, text="", font=('Arial', 12))
result_label.pack(pady=10)

# Run the application
root.mainloop()
