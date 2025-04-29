import subprocess
import tkinter as tk
from tkinter import scrolledtext


def get_wifi_passwords():
    # Clear the output area
    output_area.delete(1.0, tk.END)

    try:
        # Get all WiFi profiles
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
        profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]

        # Display header
        output_area.insert(tk.END, f"{'WiFi Name':<30}| {'Password'}\n")
        output_area.insert(tk.END, "-" * 50 + "\n")

        # Get and display passwords for each profile
        for profile in profiles:
            try:
                results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode(
                    'utf-8').split('\n')
                results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
                output_area.insert(tk.END, f"{profile:<30}| {results[0] if results else ''}\n")
            except IndexError:
                output_area.insert(tk.END, f"{profile:<30}| \n")
            except subprocess.CalledProcessError:
                output_area.insert(tk.END, f"{profile:<30}| ENCODING ERROR\n")

    except Exception as e:
        output_area.insert(tk.END, f"Error: {str(e)}\n")


# Create the main window
root = tk.Tk()
root.title("WiFi Password Viewer")
root.geometry("600x400")

# Create a frame for the button
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Create the button to get passwords
get_passwords_btn = tk.Button(button_frame, text="Get WiFi Passwords", command=get_wifi_passwords)
get_passwords_btn.pack()

# Create a scrolled text area for output
output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
output_area.pack(padx=10, pady=10)

# Run the application
root.mainloop()
