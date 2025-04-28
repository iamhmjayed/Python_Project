# Project_5_Jarvis_AI with Tkinter GUI

import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import tkinter as tk
from tkinter import scrolledtext, ttk
from threading import Thread


class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis AI Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e1e')

        # Initialize engine
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)

        # Create GUI elements
        self.create_widgets()

        # Start with welcome message
        self.wish_me()

    def create_widgets(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg='#1e1e1e')
        header_frame.pack(pady=10)

        self.logo_label = tk.Label(header_frame, text="JARVIS", font=("Helvetica", 24, "bold"),
                                   fg="#00ff00", bg='#1e1e1e')
        self.logo_label.pack()

        # Status Frame
        status_frame = tk.Frame(self.root, bg='#1e1e1e')
        status_frame.pack(pady=5)

        self.status_label = tk.Label(status_frame, text="Status: Ready", font=("Helvetica", 12),
                                     fg="white", bg='#1e1e1e')
        self.status_label.pack()

        # Console Frame
        console_frame = tk.Frame(self.root, bg='#1e1e1e')
        console_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, width=80, height=20,
                                                 font=("Consolas", 10), bg='#2d2d2d', fg='white',
                                                 insertbackground='white')
        self.console.pack(fill=tk.BOTH, expand=True)
        self.console.insert(tk.END, "Initializing Jarvis AI...\n")
        self.console.configure(state='disabled')

        # Button Frame
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(pady=10)

        self.listen_btn = ttk.Button(button_frame, text="Start Listening", command=self.start_listening_thread)
        self.listen_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_listening, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.exit_btn = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        self.exit_btn.pack(side=tk.LEFT, padx=5)

    def update_console(self, text):
        self.console.configure(state='normal')
        self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END)
        self.console.configure(state='disabled')

    def speak(self, audio):
        self.update_console(f"Jarvis: {audio}")
        self.engine.say(audio)
        self.engine.runAndWait()

    def wish_me(self):
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 12:
            greeting = "Good Morning!"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"

        self.speak(f"{greeting} I am Jarvis Sir. Please tell me how may I help you")

    def start_listening_thread(self):
        self.listen_thread = Thread(target=self.main_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.listen_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Listening...")

    def stop_listening(self):
        self.listening = False
        self.listen_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Ready")

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_console("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source)

        try:
            self.update_console("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            self.update_console(f"User said: {query}")
            return query.lower()
        except Exception as e:
            self.update_console("Say that again please...")
            return "none"

    def send_email(self, to, content):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login('youremail@gmail.com', 'your-password')
            server.sendmail('youremail@gmail.com', to, content)
            server.close()
            return True
        except Exception as e:
            self.update_console(f"Error sending email: {e}")
            return False

    def main_loop(self):
        self.listening = True
        while self.listening:
            query = self.take_command()

            if not self.listening:
                break

            if query == "none":
                continue

            # Logic for executing tasks based on query
            if 'wikipedia' in query:
                self.speak('Searching Wikipedia...')
                query = query.replace("wikipedia", "")
                results = wikipedia.summary(query, sentences=2)
                self.speak("According to Wikipedia")
                self.update_console(results)

            elif 'open youtube' in query:
                webbrowser.open("youtube.com")
                self.speak("Opening YouTube")

            elif 'open google' in query:
                webbrowser.open("google.com")
                self.speak("Opening Google")

            elif 'open stackoverflow' in query:
                webbrowser.open("stackoverflow.com")
                self.speak("Opening Stack Overflow")

            elif 'play music' in query:
                music_dir = r'D:\SnapTube Audio'  # Using raw string
                songs = os.listdir(music_dir)
                self.update_console(f"Playing: {songs[0]}")
                os.startfile(os.path.join(music_dir, songs[0]))
                self.speak("Playing music")

            elif 'the time' in query:
                str_time = datetime.datetime.now().strftime("%H:%M:%S")
                self.speak(f"Sir, the time is {str_time}")
                self.update_console(f"Current time: {str_time}")

            elif 'open code' in query:
                code_path = r"C:\Program Files\JetBrains\PyCharm 2024.1.3\bin\pycharm64.exe"  # Using raw string
                os.startfile(code_path)
                self.speak("Opening PyCharm")

            elif 'open gmail' in query:
                try:
                    self.speak("What should I say?")
                    content = self.take_command()
                    to = "jayed2305101640@diu.edu.bd"
                    if self.send_email(to, content):
                        self.speak("Email has been sent!")
                    else:
                        self.speak("Sorry, I was not able to send this email")
                except Exception as e:
                    self.update_console(f"Error: {e}")
                    self.speak("Sorry my friend Jayed. I am not able to send this email")

            elif 'exit' in query or 'quit' in query or 'goodbye' in query:
                self.speak("Goodbye Sir. Have a nice day!")
                self.root.quit()
                break


def main():
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
