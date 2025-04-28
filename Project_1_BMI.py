#Project_1 : BODY MASS INDEX (BMI)

import tkinter as tk
from tkinter import messagebox


def calculate_bmi():
    name = name_entry.get()
    age = age_entry.get()
    if not name or not age:
        messagebox.showerror("Error", "Please enter both name and age")
        return

    try:
        height = float(height_entry.get())
        weight = float(weight_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for height and weight")
        return

    height_in_m = height / 100
    bmi = weight / (height_in_m * height_in_m)
    bmi_result.set(f"{name}, Your BMI is: {bmi:.2f}")

    if bmi <= 18.4:
        target_weight = 18.5 * (height_in_m * height_in_m)
        weight_diff = target_weight - weight
        if weight_diff > 0:
            advice = f"{name}, You need to gain {weight_diff:.2f} kg to reach BMI of 18.5."
        elif weight_diff < 0:
            advice = f"{name}, You need to lose {abs(weight_diff):.2f} kg to reach BMI of 18.5."
        else:
            advice = f"{name}, You are already at the perfect BMI."
        category = "Underweight"

    elif bmi <= 24.9:
        advice = f"{name}, You are Normal. GOOD JOB"
        category = "Normal weight"

    elif bmi <= 39.9:
        target_weight = 24.9 * (height_in_m * height_in_m)
        weight_diff = target_weight - weight
        if weight_diff > 0:
            advice = f"{name}, You need to gain {weight_diff:.2f} kg to reach BMI of 24.9."
        elif weight_diff < 0:
            advice = f"{name}, You need to lose {abs(weight_diff):.2f} kg to reach BMI of 24.9."
        else:
            advice = f"{name}, You are already at the perfect BMI."
        category = "Overweight"

    else:
        target_weight = 24.9 * (height_in_m * height_in_m)
        weight_diff = target_weight - weight
        if weight_diff > 0:
            advice = f"{name}, You need to gain {weight_diff:.2f} kg to reach BMI of 24.9."
        elif weight_diff < 0:
            advice = f"{name}, You need to lose {abs(weight_diff):.2f} kg to reach BMI of 24.9."
        else:
            advice = f"{name}, You are already at the perfect BMI."
        category = "Obese"

    advice_result.set(advice)
    category_result.set(f"Category: {category}")


# Create main window
root = tk.Tk()
root.title("BMI Calculator")
root.geometry("400x400")

# Welcome label
welcome_label = tk.Label(root, text="Welcome to BMI Calculator", font=("Arial", 14, "bold"))
welcome_label.pack(pady=10)

# Name entry
name_frame = tk.Frame(root)
name_frame.pack(pady=5)
tk.Label(name_frame, text="Name:").pack(side=tk.LEFT)
name_entry = tk.Entry(name_frame)
name_entry.pack(side=tk.LEFT, padx=5)

# Age entry
age_frame = tk.Frame(root)
age_frame.pack(pady=5)
tk.Label(age_frame, text="Age:").pack(side=tk.LEFT)
age_entry = tk.Entry(age_frame)
age_entry.pack(side=tk.LEFT, padx=5)

# Height entry
height_frame = tk.Frame(root)
height_frame.pack(pady=5)
tk.Label(height_frame, text="Height (cm):").pack(side=tk.LEFT)
height_entry = tk.Entry(height_frame)
height_entry.pack(side=tk.LEFT, padx=5)

# Weight entry
weight_frame = tk.Frame(root)
weight_frame.pack(pady=5)
tk.Label(weight_frame, text="Weight (kg):").pack(side=tk.LEFT)
weight_entry = tk.Entry(weight_frame)
weight_entry.pack(side=tk.LEFT, padx=5)

# Calculate button
calculate_btn = tk.Button(root, text="Calculate BMI", command=calculate_bmi)
calculate_btn.pack(pady=10)

# Results
bmi_result = tk.StringVar()
bmi_label = tk.Label(root, textvariable=bmi_result, font=("Arial", 12))
bmi_label.pack(pady=5)

category_result = tk.StringVar()
category_label = tk.Label(root, textvariable=category_result, font=("Arial", 12))
category_label.pack(pady=5)

advice_result = tk.StringVar()
advice_label = tk.Label(root, textvariable=advice_result, font=("Arial", 10), wraplength=350)
advice_label.pack(pady=5)

root.mainloop()
