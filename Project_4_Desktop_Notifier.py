from tkinter import simpledialog, Tk, messagebox
import tkinter as tk
from plyer import notification


def show_notification():
    try:
        root = Tk()
        root.withdraw()
        a = simpledialog.askstring("Input", "What is your name?", parent=root)

        if a:
            notification.notify(
                title="Learning Time",
                message=f"Hello {a}. It's Time to learn Something new",
                timeout=5
            )
        else:
            messagebox.showwarning("Warning", "You didn't enter a name!")

        root.destroy()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    show_notification()
