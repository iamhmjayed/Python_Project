import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
from tkinter.font import Font
import sys
import platform
import threading
import webbrowser
from PIL import ImageTk, Image


class PythonIDE:
    def __init__(self, root):
        # Set up the main window
        self.root = root
        self.root.title("ZAYEDs PYTHON IDE")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)

        # Track the current file and running process
        self.current_file = None
        self.unsaved_changes = False
        self.process = None
        self.waiting_for_input = False

        # Set up colors and fonts
        self.setup_appearance()

        # Build the user interface
        self.create_interface()

        # Set up keyboard shortcuts
        self.setup_shortcuts()

    def setup_appearance(self):
        """Configure colors and fonts for the IDE"""
        # Background gradient colors
        self.bg_colors = ["#1E90FF", "#00BFFF", "#FF8C00", "#FFA500"]

        # Editor colors
        self.editor_bg = "#FFFFFF"
        self.editor_fg = "#333333"

        # Input/output colors
        self.io_bg = "#F5F5F5"

        # Section header colors
        self.header_colors = {
            "editor": "#1E90FF",
            "output": "#FF8C00",
            "input": "#4CAF50"
        }

        # Fonts
        self.title_font = Font(family="Helvetica", size=24, weight="bold")
        self.section_font = Font(family="Segoe UI", size=12, weight="bold")
        self.button_font = Font(family="Segoe UI", size=11)
        self.editor_font = Font(family="Consolas", size=14)
        self.output_font = Font(family="Consolas", size=12)

    def create_interface(self):
        """Build all parts of the user interface"""
        # Create the gradient background
        self.create_background()

        # Main container frame
        self.main_frame = tk.Frame(self.root, bg="#F5F5F5", bd=2, relief=tk.RAISED)
        self.main_frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)

        # Add title and subtitle
        self.create_header()

        # Create the menu bar
        self.create_menus()

        # Create the toolbar with buttons
        self.create_toolbar()

        # Create the editor and output panels
        self.create_editor_panel()
        self.create_output_panel()

        # Create the status bar
        self.create_status_bar()

    def create_background(self):
        """Draw the gradient background"""
        bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        bg_canvas.pack(fill="both", expand=True)

        # Calculate size for each color segment
        height_per_color = 800 / len(self.bg_colors)

        # Draw each color segment
        for i, color in enumerate(self.bg_colors):
            y1 = i * height_per_color
            y2 = (i + 1) * height_per_color
            bg_canvas.create_rectangle(0, y1, 1400, y2, fill=color, outline="")

    def create_header(self):
        """Create the header with logo and title"""
        # Header frame
        self.header = tk.Frame(self.main_frame, bg="#F5F5F5")
        self.header.pack(fill=tk.X, pady=5)

        # Container for logo and title
        title_container = tk.Frame(self.header, bg="#F5F5F5")
        title_container.pack(expand=True)

        # Add logo
        try:
            logo_path = "ZAYED_PYTHON_IDE.png"  # Make sure this file exists in your directory
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((40, 40), Image.LANCZOS)  # Resize as needed
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(
                    title_container,
                    image=self.logo_photo,
                    bg="#F5F5F5"
                )
                logo_label.image = self.logo_photo  # Keep reference
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
            else:
                raise FileNotFoundError(f"Logo file not found at {logo_path}")
        except Exception as e:
            print(f"Logo error: {str(e)}")
            # Fallback to text if image fails
            logo_label = tk.Label(
                title_container,
                text="[LOGO]",
                bg="#F5F5F5",
                fg="red"
            )
            logo_label.pack(side=tk.LEFT)

        # Main title
        title = tk.Label(
            title_container,
            text="ZAYED PYTHON IDE",
            font=self.title_font,
            fg=self.header_colors["editor"],
            bg="#F5F5F5"
        )
        title.pack(side=tk.LEFT)

        # Subtitle
        subtitle = tk.Label(
            self.header,
            text="Professional Python Development Environment",
            font=("Segoe UI", 10),
            fg="#666666",
            bg="#F5F5F5"
        )
        subtitle.pack(expand=True)

    def create_menus(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Run", command=self.run_code, accelerator="Ctrl+R")
        run_menu.add_command(label="Stop", command=self.stop_execution)
        run_menu.add_command(label="Debug", command=self.debug_code, accelerator="F5")
        menubar.add_cascade(label="Run", menu=run_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def create_toolbar(self):
        """Create the toolbar with buttons"""
        toolbar = tk.Frame(self.main_frame, bg="#F5F5F5")
        toolbar.pack(fill="x", pady=(0, 10))

        # Button style settings
        button_style = {
            "font": self.button_font,
            "bd": 0,
            "padx": 12,
            "pady": 5,
            "activebackground": "#E0E0E0",
            "highlightthickness": 0
        }

        # File operation buttons
        self.create_toolbar_button(toolbar, "New", self.new_file, "#1E90FF", button_style)
        self.create_toolbar_button(toolbar, "Open", self.open_file, "#1E90FF", button_style)
        self.create_toolbar_button(toolbar, "Save", self.save_file, "#1E90FF", button_style)
        self.create_toolbar_button(toolbar, "Save As", self.save_as_file, "#1E90FF", button_style)

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)

        # Execution buttons
        self.create_toolbar_button(toolbar, "Run", self.run_code, "#4CAF50", button_style)
        self.create_toolbar_button(toolbar, "Debug", self.debug_code, "#FF9800", button_style)
        self.create_toolbar_button(toolbar, "Stop", self.stop_execution, "#F44336", button_style)
        self.create_toolbar_button(toolbar, "Clear", self.clear_output, "#9E9E9E", button_style)

        # Help button on right
        self.create_toolbar_button(toolbar, "Help", self.show_help, "#9C27B0", button_style, "right")

    def create_toolbar_button(self, parent, text, command, color, style, side="left"):
        """Helper to create consistent toolbar buttons"""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            **style
        )
        button.pack(side=side, padx=5)
        return button

    def create_editor_panel(self):
        """Create the code editor section"""
        # Use PanedWindow for resizable panels
        self.panes = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, sashwidth=8)
        self.panes.pack(fill="both", expand=True)

        # Editor frame
        editor_frame = tk.Frame(self.panes, bg="#F5F5F5")

        # Editor header
        editor_header = tk.Label(
            editor_frame,
            text="PYTHON CODE EDITOR",
            font=self.section_font,
            bg=self.header_colors["editor"],
            fg="white",
            padx=10,
            pady=5
        )
        editor_header.pack(fill="x", pady=(0, 5))

        # Editor container with line numbers
        editor_container = tk.Frame(editor_frame, bg=self.editor_bg)
        editor_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Line numbers
        self.line_numbers = tk.Text(
            editor_container,
            width=4,
            padx=5,
            pady=10,
            bg="#E0E0E0",
            fg="#333333",
            state="disabled",
            font=self.editor_font
        )
        self.line_numbers.pack(side="left", fill="y")

        # Main editor
        self.editor = scrolledtext.ScrolledText(
            editor_container,
            font=self.editor_font,
            wrap=tk.NONE,
            undo=True,
            padx=10,
            pady=10,
            bg=self.editor_bg,
            fg=self.editor_fg
        )
        self.editor.pack(side="left", fill="both", expand=True)

        # Set up line number updates
        self.editor.bind("<KeyRelease>", lambda e: self.update_line_numbers())
        self.editor.bind("<MouseWheel>", lambda e: self.update_line_numbers())

        # Error highlighting
        self.editor.tag_configure("error", background="#FFDDDD", foreground="red")

        self.panes.add(editor_frame, minsize=600)

    def create_output_panel(self):
        """Create the output section"""
        output_frame = tk.Frame(self.panes, bg="#F5F5F5")

        # Output header
        output_header = tk.Label(
            output_frame,
            text="PROGRAM OUTPUT",
            font=self.section_font,
            bg=self.header_colors["output"],
            fg="white",
            padx=10,
            pady=5
        )
        output_header.pack(fill="x", pady=(0, 5))

        # Output text area
        self.output = scrolledtext.ScrolledText(
            output_frame,
            font=self.output_font,
            state="normal",
            bg=self.io_bg,
            fg="#333333",
            padx=10,
            pady=10
        )
        self.output.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        # Input section (hidden by default)
        self.input_header = tk.Label(
            output_frame,
            text="PROGRAM INPUT",
            font=self.section_font,
            bg=self.header_colors["input"],
            fg="white",
            padx=10,
            pady=5
        )

        self.input_entry = tk.Text(
            output_frame,
            font=self.output_font,
            bg=self.io_bg,
            height=5,
            padx=10,
            pady=10
        )

        self.input_button = tk.Button(
            output_frame,
            text="SUBMIT INPUT",
            command=self.submit_input,
            bg=self.header_colors["input"],
            fg="white",
            font=self.button_font,
            padx=20,
            pady=5
        )

        self.panes.add(output_frame, minsize=600)

    def create_status_bar(self):
        """Create the status bar at bottom"""
        self.status_bar = tk.Label(
            self.main_frame,
            text="Ready | Zayed Python IDE | Ctrl+S to Save | Ctrl+R to Run | F5 to Debug",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Segoe UI", 9),
            bg="#1E90FF",
            fg="white"
        )
        self.status_bar.pack(fill="x", pady=(5, 0))

    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        shortcuts = {
            "<Control-s>": self.save_file,
            "<Control-o>": self.open_file,
            "<Control-r>": self.run_code,
            "<F5>": self.debug_code,
            "<Control-n>": self.new_file,
            "<Control-z>": self.undo,
            "<Control-y>": self.redo,
            "<Control-x>": self.cut,
            "<Control-c>": self.copy,
            "<Control-v>": self.paste,
            "<Control-a>": self.select_all,
            "<F1>": self.show_help
        }

        for key, command in shortcuts.items():
            self.root.bind(key, lambda e, cmd=command: cmd())

    # File operations
    def new_file(self):
        """Create a new empty file"""
        if self.unsaved_changes:
            if not messagebox.askyesno("Unsaved Changes", "Save current file first?"):
                return
            self.save_file()

        self.editor.delete("1.0", tk.END)
        self.current_file = None
        self.unsaved_changes = False
        self.root.title("ZAYED PYTHON IDE")
        self.status_bar.config(text="New file created")

    def open_file(self):
        """Open an existing Python file"""
        if self.unsaved_changes:
            if not messagebox.askyesno("Unsaved Changes", "Save current file first?"):
                return
            self.save_file()

        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, file.read())

            self.current_file = file_path
            self.unsaved_changes = False
            self.root.title(f"{os.path.basename(file_path)} - ZAYED PYTHON IDE")
            self.status_bar.config(text=f"Opened: {file_path}")
            self.update_line_numbers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, "w") as file:
                    file.write(self.editor.get("1.0", tk.END))

                self.unsaved_changes = False
                self.root.title(f"{os.path.basename(self.current_file)} - ZAYED PYTHON IDE")
                self.status_bar.config(text=f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save with a new filename"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w") as file:
                file.write(self.editor.get("1.0", tk.END))

            self.current_file = file_path
            self.unsaved_changes = False
            self.root.title(f"{os.path.basename(file_path)} - ZAYED PYTHON IDE")
            self.status_bar.config(text=f"Saved as: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    # Edit functions
    def undo(self):
        """Undo the last edit"""
        try:
            self.editor.edit_undo()
        except:
            pass

    def redo(self):
        """Redo the last undone edit"""
        try:
            self.editor.edit_redo()
        except:
            pass

    def cut(self):
        """Cut selected text"""
        self.editor.event_generate("<<Cut>>")

    def copy(self):
        """Copy selected text"""
        self.editor.event_generate("<<Copy>>")

    def paste(self):
        """Paste from clipboard"""
        self.editor.event_generate("<<Paste>>")

    def select_all(self):
        """Select all text in editor"""
        self.editor.tag_add("sel", "1.0", "end")
        return "break"

    # Code execution
    def run_code(self):
        """Run the current Python code"""
        if not self.editor.get("1.0", "end-1c").strip():
            self.status_bar.config(text="No code to run")
            return

        if self.unsaved_changes:
            if not messagebox.askyesno("Unsaved Changes", "Save before running?"):
                return
            self.save_file()

        self.status_bar.config(text="Running...")
        self.clear_output()
        self.append_output(">>> Running program...\n")

        # Hide input widgets initially
        self.hide_input_widgets()

        # Clear any existing error highlights
        self.editor.tag_remove("error", "1.0", "end")

        # Save to temp file if needed
        if not self.current_file:
            temp_file = "temp.py"
            with open(temp_file, "w") as f:
                f.write(self.editor.get("1.0", tk.END))
            file_to_run = temp_file
        else:
            file_to_run = self.current_file

        # Start the Python process
        self.process = subprocess.Popen(
            [sys.executable, file_to_run],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Start thread to read output
        threading.Thread(target=self.read_process_output, daemon=True).start()

    def debug_code(self):
        """Debug the code (same as run for now)"""
        self.run_code()

    def stop_execution(self):
        """Stop the currently running program"""
        if self.process:
            try:
                if platform.system() == "Windows":
                    self.process.terminate()
                else:
                    self.process.kill()
                self.status_bar.config(text="Execution stopped")
            except:
                self.status_bar.config(text="Error stopping execution")

    def read_process_output(self):
        """Read output from the running process"""
        while True:
            output = self.process.stdout.readline()
            if not output and self.process.poll() is not None:
                break
            if output:
                self.root.after(0, self.append_output, output)

        # Handle any errors
        errors = self.process.stderr.read()
        if errors:
            formatted_error = self.format_error(errors)
            self.root.after(0, self.append_error, formatted_error)

            # Try to highlight error line
            line_number = self.find_error_line(errors)
            if line_number:
                self.root.after(0, self.highlight_error_line, line_number)

        # Clean up
        return_code = self.process.poll()
        self.root.after(0, self.execution_finished, return_code)

        # Remove temp file if used
        if not self.current_file and os.path.exists("temp.py"):
            os.remove("temp.py")

    def format_error(self, error_msg):
        """Format error message for display"""
        lines = error_msg.split('\n')
        formatted = []

        for line in lines:
            if line.strip().startswith("File"):
                parts = line.split(',')
                if len(parts) >= 2:
                    formatted.append(f"🔴 {parts[0].strip()}, {parts[1].strip()}")
                else:
                    formatted.append(f"🔴 {line}")
            elif "Error:" in line or "Exception:" in line:
                formatted.append(f"❌ ERROR: {line.split(':')[-1].strip()}")
            elif line.strip():
                formatted.append(f"    {line}")

        return '\n'.join(formatted)

    def find_error_line(self, error_msg):
        """Find the line number from an error message"""
        for line in error_msg.split('\n'):
            if "line " in line and ("File" in line or "file" in line):
                try:
                    return int(line.split('line ')[1].split(',')[0].strip())
                except:
                    continue
        return None

    def highlight_error_line(self, line_number):
        """Highlight the line with an error"""
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"
        self.editor.tag_add("error", line_start, line_end)
        self.editor.see(line_start)

    def execution_finished(self, return_code):
        """Handle program completion"""
        self.process = None
        if return_code == 0:
            self.status_bar.config(text="Execution completed successfully")
        else:
            self.status_bar.config(text=f"Execution failed with code {return_code}")

    # Output handling
    def clear_output(self):
        """Clear the output panel"""
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.config(state="disabled")
        self.status_bar.config(text="Output cleared")

    def append_output(self, text):
        """Add text to the output panel"""
        self.output.config(state="normal")
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state="disabled")

        # Check for input requests
        if "input(" in text or "input (" in text:
            self.waiting_for_input = True
            self.show_input_widgets()
            self.status_bar.config(text="Waiting for input...")
            self.input_entry.focus()

    def append_error(self, text):
        """Add error message to output"""
        self.output.config(state="normal")
        self.output.insert(tk.END, "❌ ERROR OUTPUT:\n", "error")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.config(state="disabled")

    def show_input_widgets(self):
        """Show the input widgets"""
        self.input_header.pack(fill="x", pady=(10, 5))
        self.input_entry.pack(fill="x", padx=5, pady=(0, 5))
        self.input_button.pack(pady=(0, 10))

    def hide_input_widgets(self):
        """Hide the input widgets"""
        self.input_header.pack_forget()
        self.input_entry.pack_forget()
        self.input_button.pack_forget()

    def submit_input(self):
        """Send user input to running program"""
        if self.waiting_for_input and self.process:
            user_input = self.input_entry.get("1.0", tk.END)
            self.input_entry.delete("1.0", tk.END)

            try:
                self.process.stdin.write(user_input)
                self.process.stdin.flush()
                self.waiting_for_input = False
                self.hide_input_widgets()
                self.status_bar.config(text="Input submitted")
            except:
                self.status_bar.config(text="Error submitting input")

    def update_line_numbers(self):
        """Update the line numbers in the editor"""
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)

        # Count lines in editor
        line_count = self.editor.get(1.0, tk.END).count('\n')

        # Add line numbers
        for line in range(1, line_count + 2):
            self.line_numbers.insert(tk.END, f"{line}\n")

        self.line_numbers.config(state="disabled")

    # Help and about
    def show_help(self):
        """Show help information"""
        help_text = """ZAYED PYTHON IDE - HELP

Shortcuts:
Ctrl+N - New File
Ctrl+O - Open File
Ctrl+S - Save File
Ctrl+R - Run Program
F5 - Debug Mode
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+X - Cut
Ctrl+C - Copy
Ctrl+V - Paste
Ctrl+A - Select All
F1 - Show Help

For Python documentation, visit: python.org
"""
        messagebox.showinfo("Help", help_text)
        webbrowser.open("https://docs.python.org/3/")

    def show_about(self):
        """Show about dialog"""
        about_text = """ZAYED PYTHON IDE

Version: 2.0
Developed by: Hossain Mohammad Jayed

A professional Python development environment.
Contact: jayed2305101640@diu.edu.bd
"""
        messagebox.showinfo("About", about_text)


# Start the application
if __name__ == "__main__":
    root = tk.Tk()

    # Try to set window icon
    try:
        if platform.system() == "Windows":
            root.iconbitmap(default="python.ico")
        else:
            img = tk.PhotoImage(file="python.png")
            root.tk.call("wm", "iconphoto", root._w, img)
    except:
        pass

    # Create and run the IDE
    ide = PythonIDE(root)
    root.mainloop()
