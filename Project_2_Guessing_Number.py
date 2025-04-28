#Project_2(GUESSING THE NUMBER)

import random
import tkinter as tk
from tkinter import messagebox

def check_guess():
    try:
        userinput = int(guess_entry.get())
        randomnumber = int(random_label.cget("text").split(": ")[1])  # Get the random number from the hidden label
        
        if userinput > randomnumber:
            result_label.config(text=f"Your Guessed Number is {userinput}\nThe Number is Too high")
            messagebox.showinfo("Result", f"Too high!\n\n:) TRY AGAIN BEST OF LUCK {name.get()} ;)")
        elif userinput < randomnumber:
            result_label.config(text=f"Your Guessed Number is {userinput}\nThe Number is Too low")
            messagebox.showinfo("Result", f"Too low!\n\n:) TRY AGAIN BEST OF LUCK {name.get()} ;)")
        else:
            result_label.config(text=f"Your Guessed Number is {userinput}\nCorrect!")
            messagebox.showinfo("Result", f"BINGO CONGRATULATIONS {name.get()}!\n\nYou guessed it right!")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number between 1 and 50")

def start_game():
    if not name.get():
        messagebox.showerror("Error", "Please enter your name first")
        return
    
    welcome_label.config(text=f"Welcome {name.get()} to Guessing The Number Game")
    name_entry.pack_forget()
    name_label.pack_forget()
    start_button.pack_forget()
    
    # Generate random number and store it in the hidden label
    randomnumber = random.randint(1, 50)
    random_label.config(text=f"Random Number: {randomnumber}")
    
    guess_frame.pack(pady=10)
    guess_button.pack(pady=5)
    result_label.pack(pady=10)

# Create main window
root = tk.Tk()
root.title("Guessing The Number Game")
root.geometry("400x300")

# Name entry
name_label = tk.Label(root, text="What is your name?")
name_label.pack(pady=5)

name = tk.StringVar()
name_entry = tk.Entry(root, textvariable=name)
name_entry.pack(pady=5)

start_button = tk.Button(root, text="Start Game", command=start_game)
start_button.pack(pady=10)

# Welcome label
welcome_label = tk.Label(root, text="")
welcome_label.pack(pady=5)

# Hidden label to store the random number
random_label = tk.Label(root, text="")
random_label.pack_forget()

# Guess frame
guess_frame = tk.Frame(root)
guess_label = tk.Label(guess_frame, text="Guess The Number Between 1 to 50:")
guess_label.pack(side=tk.LEFT)

guess_entry = tk.Entry(guess_frame, width=5)
guess_entry.pack(side=tk.LEFT, padx=5)

# Guess button
guess_button = tk.Button(root, text="Check Guess", command=check_guess)

# Result label
result_label = tk.Label(root, text="", justify=tk.LEFT)
result_label.pack_forget()

root.mainloop()
