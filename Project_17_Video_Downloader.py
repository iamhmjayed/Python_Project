import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import yt_dlp
import os
import threading


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Video Downloader")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Set icon (optional)
        try:
            self.root.iconbitmap('video_icon.ico')
        except:
            pass

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Header frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=10)

        # Logo (optional)
        try:
            img = Image.open("video_icon.png").resize((64, 64))
            self.logo = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(header_frame, image=self.logo)
            logo_label.grid(row=0, column=0, padx=10)
        except:
            pass

        title_label = ttk.Label(header_frame, text="Universal Video Downloader", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=1)

        # URL input frame
        url_frame = ttk.Frame(self.root)
        url_frame.pack(pady=10, padx=20, fill=tk.X)

        ttk.Label(url_frame, text="Video URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Download options frame
        options_frame = ttk.LabelFrame(self.root, text="Download Options", padding=10)
        options_frame.pack(pady=10, padx=20, fill=tk.X)

        ttk.Label(options_frame, text="Save to:").grid(row=0, column=0, sticky=tk.W)
        self.save_path = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Downloads'))
        ttk.Entry(options_frame, textvariable=self.save_path, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(options_frame, text="Browse", command=self.browse_directory).grid(row=0, column=2)

        ttk.Label(options_frame, text="Quality:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar(value='best')
        quality_options = ['Best', '1080p', '720p', '480p', '360p', 'Audio Only']
        ttk.OptionMenu(options_frame, self.quality_var, 'Best', *quality_options).grid(row=1, column=1, sticky=tk.W)

        # Progress frame
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(pady=10, padx=20, fill=tk.X)

        self.progress_label = ttk.Label(progress_frame, text="Ready to download")
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        # Button frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Download", command=self.start_download).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_path.set(directory)

    def clear_fields(self):
        self.url_entry.delete(0, tk.END)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready to download")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return

        save_path = self.save_path.get()
        if not os.path.exists(save_path):
            messagebox.showerror("Error", "The specified directory does not exist")
            return

        # Map quality selection to yt-dlp format
        quality_map = {
            'Best': 'best',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
            'Audio Only': 'bestaudio'
        }

        format_selection = quality_map[self.quality_var.get()]

        # Start download in a separate thread to keep UI responsive
        download_thread = threading.Thread(
            target=self.download_video,
            args=(url, save_path, format_selection),
            daemon=True
        )
        download_thread.start()

    def download_video(self, url, save_path, format_selection):
        self.progress_label.config(text="Preparing download...")
        self.progress_bar['value'] = 0

        ydl_opts = {
            'format': format_selection,
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.update_progress],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.progress_label.config(text="Downloading...")
                ydl.download([url])
                self.progress_label.config(text="Download completed!")
                messagebox.showinfo("Success", "Video downloaded successfully!")
        except Exception as e:
            self.progress_label.config(text="Download failed")
            messagebox.showerror("Error", f"Download failed: {str(e)}")

    def update_progress(self, d):
        if d['status'] == 'downloading':
            percent = float(d['_percent_str'].strip('%'))
            self.progress_bar['value'] = percent
            self.progress_label.config(text=f"Downloading: {d['_percent_str']} at {d['_speed_str']}")
            self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()