import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
from tkinter.font import Font
import sys
import platform
import threading
import webbrowser
import traceback


class ZayedPythonIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("ZAYED PYTHON IDE")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)

        # Custom theme colors
        self.bg_gradient = ["#1E90FF", "#00BFFF", "#FF8C00", "#FFA500"]
        self.editor_bg = "#FFFFFF"
        self.editor_fg = "#333333"
        self.io_bg = "#F5F5F5"
        self.header_colors = {
            "editor": "#1E90FF",
            "output": "#FF8C00",
            "input": "#4CAF50"
        }

        # Setup fonts first
        self.title_font = Font(family="Helvetica", size=24, weight="bold")
        self.section_font = Font(family="Segoe UI", size=12, weight="bold")
        self.button_font = Font(family="Segoe UI", size=11)
        self.editor_font = Font(family="Consolas", size=14)
        self.output_font = Font(family="Consolas", size=12)

        # Runtime variables
        self.current_file = None
        self.unsaved_changes = False
        self.process = None
        self.waiting_for_input = False

        # Initialize UI
        self.setup_ui()

        # Bind keyboard shortcuts
        self.setup_shortcuts()

    def setup_ui(self):
        """Create the main UI components"""
        # Create gradient background
        self.create_gradient_background()

        # Main container frame
        self.main_frame = tk.Frame(self.root, bg="#F5F5F5", bd=2, relief=tk.RAISED)
        self.main_frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)

        # Header with title
        self.setup_header()

        # Menu bar
        self.setup_menu_bar()

        # Toolbar with buttons
        self.setup_toolbar()

        # Main content area - vertical split
        self.setup_content_area()

        # Status bar
        self.setup_status_bar()

    def setup_menu_bar(self):
        """Create the menu bar with all edit functions"""
        self.menu_bar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Run menu
        run_menu = tk.Menu(self.menu_bar, tearoff=0)
        run_menu.add_command(label="Run", command=self.run_code, accelerator="Ctrl+R")
        run_menu.add_command(label="Stop", command=self.stop_execution)
        run_menu.add_command(label="Debug", command=self.debug_code, accelerator="F5")
        self.menu_bar.add_cascade(label="Run", menu=run_menu)

        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=self.menu_bar)

    # ===== EDIT FUNCTIONS =====
    def undo(self):
        """Undo the last action"""
        try:
            self.editor.edit_undo()
        except:
            pass

    def redo(self):
        """Redo the last undone action"""
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

    # ===== FILE OPERATIONS =====
    def new_file(self):
        """Create a new file"""
        if self.unsaved_changes:
            if not messagebox.askyesno("Unsaved Changes", "Save current file before creating new one?"):
                return
            self.save_file()

        self.editor.delete("1.0", tk.END)
        self.current_file = None
        self.unsaved_changes = False
        self.root.title("Zayed Python IDE")
        self.status_bar.config(text="New file created")

    def open_file(self):
        """Open an existing file"""
        if self.unsaved_changes:
            if not messagebox.askyesno("Unsaved Changes", "Save current file before opening another?"):
                return
            self.save_file()

        file_path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as file:
                    self.editor.delete("1.0", tk.END)
                    self.editor.insert(tk.END, file.read())
                self.current_file = file_path
                self.unsaved_changes = False
                self.root.title(f"{os.path.basename(file_path)} - Zayed Python IDE")
                self.status_bar.config(text=f"Opened: {file_path}")
                self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, "w") as file:
                    file.write(self.editor.get("1.0", tk.END))
                self.unsaved_changes = False
                self.root.title(f"{os.path.basename(self.current_file)} - Zayed Python IDE")
                self.status_bar.config(text=f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w") as file:
                    file.write(self.editor.get("1.0", tk.END))
                self.current_file = file_path
                self.unsaved_changes = False
                self.root.title(f"{os.path.basename(file_path)} - Zayed Python IDE")
                self.status_bar.config(text=f"Saved as: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    # ===== EXECUTION FUNCTIONS =====
    def run_code(self):
        """Execute the current Python code with enhanced error handling"""
        if not self.editor.get("1.0", "end-1c").strip():
            self.status_bar.config(text="No code to run")
            return

        if self.unsaved_changes:
            if not messagebox.askyesno("Unsaved Changes", "Save before running?"):
                return
            self.save_file()

        self.status_bar.config(text="Running...")
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, ">>> Running program...\n")
        self.output.config(state="disabled")

        # Hide input widgets initially
        self.hide_input_widgets()

        # Remove any existing error highlights
        self.editor.tag_remove("error", "1.0", "end")

        # Save to temp file if no file saved yet
        if not self.current_file:
            temp_file = "zayed_temp.py"
            with open(temp_file, "w") as f:
                f.write(self.editor.get("1.0", tk.END))
            file_to_run = temp_file
        else:
            file_to_run = self.current_file

        # Start execution in a separate thread
        self.process = subprocess.Popen(
            [sys.executable, file_to_run],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Start thread to read output
        threading.Thread(target=self.read_output, daemon=True).start()

    def debug_code(self):
        """Run code in debug mode with more detailed error reporting"""
        self.run_code()  # Currently same as run but can be enhanced

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

    # ===== ERROR HANDLING AND DEBUGGING =====
    def read_output(self):
        """Read output from the running process with enhanced error handling"""
        while True:
            output = self.process.stdout.readline()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                self.root.after(0, self.append_output, output)

        # Enhanced error handling
        errors = self.process.stderr.read()
        if errors:
            # Format the error message with line numbers and traceback
            formatted_error = self.format_error_message(errors)
            self.root.after(0, self.append_error, formatted_error)

            # Try to extract line number from error
            line_number = self.extract_line_number(errors)
            if line_number:
                self.root.after(0, self.highlight_error_line, line_number)

        # Clean up
        return_code = self.process.poll()
        self.root.after(0, self.execution_finished, return_code)

        # Remove temp file if used
        if not self.current_file:
            try:
                os.remove("zayed_temp.py")
            except:
                pass

    def format_error_message(self, error_msg):
        """Format the error message to be more readable"""
        lines = error_msg.split('\n')
        formatted = []

        for line in lines:
            if line.strip().startswith("File"):
                # Format file/line number references
                parts = line.split(',')
                if len(parts) >= 2:
                    file_part = parts[0].strip()
                    line_part = parts[1].strip()
                    formatted.append(f"🔴 {file_part}, {line_part}")
                else:
                    formatted.append(f"🔴 {line}")
            elif "Error:" in line or "Exception:" in line:
                # Highlight error types
                formatted.append(f"❌ ERROR: {line.split(':')[-1].strip()}")
            elif line.strip():
                formatted.append(f"    {line}")

        return '\n'.join(formatted)

    def extract_line_number(self, error_msg):
        """Extract the line number from error message if possible"""
        lines = error_msg.split('\n')
        for line in lines:
            if "line " in line and ("File" in line or "file" in line):
                try:
                    # Extract line number from strings like:
                    # "File "zayed_temp.py", line 5"
                    parts = line.split(',')
                    for part in parts:
                        if "line " in part:
                            return int(part.split('line ')[1].strip())
                except:
                    continue
        return None

    def highlight_error_line(self, line_number):
        """Highlight the line where error occurred in the editor"""
        # Remove any existing error highlights
        self.editor.tag_remove("error", "1.0", "end")

        # Configure error highlight style
        self.editor.tag_configure("error", background="#FFDDDD", foreground="red")

        # Highlight the line
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"
        self.editor.tag_add("error", line_start, line_end)

        # Scroll to the line
        self.editor.see(line_start)

    # ===== UI SETUP CONTINUED =====
    def create_gradient_background(self):
        """Create the vibrant gradient background"""
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)

        for i, color in enumerate(self.bg_gradient):
            self.bg_canvas.create_rectangle(
                0, i * (800 / len(self.bg_gradient)),
                1400, (i + 1) * (800 / len(self.bg_gradient)),
                fill=color, outline="", tags="bg"
            )

    def setup_header(self):
        """Create the header with title"""
        self.header = tk.Frame(self.main_frame, bg="#F5F5F5")
        self.header.pack(fill="x", pady=(10, 15))

        self.title_label = tk.Label(
            self.header,
            text="ZAYED PYTHON IDE",
            font=self.title_font,
            fg=self.header_colors["editor"],
            bg="#F5F5F5"
        )
        self.title_label.pack(expand=True)

        # Add subtitle
        self.subtitle = tk.Label(
            self.header,
            text="Professional Python Development Environment",
            font=("Segoe UI", 10),
            fg="#666666",
            bg="#F5F5F5"
        )
        self.subtitle.pack(expand=True)

    def setup_toolbar(self):
        """Create the toolbar with action buttons"""
        self.toolbar = tk.Frame(self.main_frame, bg="#F5F5F5")
        self.toolbar.pack(fill="x", pady=(0, 10))

        # Button style
        btn_style = {
            "font": self.button_font,
            "bd": 0,
            "padx": 12,
            "pady": 5,
            "activebackground": "#E0E0E0",
            "highlightthickness": 0
        }

        # File operations
        file_buttons = [
            ("New", self.new_file, "#1E90FF"),
            ("Open", self.open_file, "#1E90FF"),
            ("Save", self.save_file, "#1E90FF"),
            ("Save As", self.save_as_file, "#1E90FF")
        ]

        for text, command, color in file_buttons:
            btn = tk.Button(
                self.toolbar,
                text=text,
                command=command,
                bg=color,
                fg="white",
                **btn_style
            )
            btn.pack(side="left", padx=5)

        # Separator
        ttk.Separator(self.toolbar, orient="vertical").pack(side="left", fill="y", padx=5)

        # Execution controls
        exec_buttons = [
            ("Run", self.run_code, "#4CAF50"),
            ("Debug", self.debug_code, "#FF9800"),
            ("Stop", self.stop_execution, "#F44336"),
            ("Clear", self.clear_output, "#9E9E9E")
        ]

        for text, command, color in exec_buttons:
            btn = tk.Button(
                self.toolbar,
                text=text,
                command=command,
                bg=color,
                fg="white",
                **btn_style
            )
            btn.pack(side="left", padx=5)

        # Help button on right
        self.help_btn = tk.Button(
            self.toolbar,
            text="Help",
            command=self.show_help,
            bg="#9C27B0",
            fg="white",
            **btn_style
        )
        self.help_btn.pack(side="right", padx=5)

    def setup_content_area(self):
        """Create the editor and IO panels"""
        self.content = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, sashwidth=8)
        self.content.pack(fill="both", expand=True)

        # Left panel - Editor
        self.setup_editor_panel()

        # Right panel - Input/Output
        self.setup_io_panel()

    def setup_editor_panel(self):
        """Create the code editor panel"""
        self.editor_panel = tk.Frame(self.content, bg="#F5F5F5")

        # Editor header
        self.editor_header = tk.Label(
            self.editor_panel,
            text="PYTHON CODE EDITOR",
            font=self.section_font,
            bg=self.header_colors["editor"],
            fg="white",
            padx=10,
            pady=5
        )
        self.editor_header.pack(fill="x", pady=(0, 5))

        # Editor container
        self.editor_container = tk.Frame(self.editor_panel, bg=self.editor_bg)
        self.editor_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Line numbers
        self.line_numbers = tk.Text(
            self.editor_container,
            width=4,
            padx=5,
            pady=10,
            bg="#E0E0E0",
            fg="#333333",
            state="disabled",
            font=self.editor_font,
            takefocus=0,
            bd=0
        )
        self.line_numbers.pack(side="left", fill="y")

        # Main editor
        self.editor = scrolledtext.ScrolledText(
            self.editor_container,
            font=self.editor_font,
            wrap=tk.NONE,
            undo=True,
            padx=10,
            pady=10,
            bg=self.editor_bg,
            fg=self.editor_fg,
            insertbackground=self.editor_fg,
            selectbackground="#1E90FF"
        )
        self.editor.pack(side="left", fill="both", expand=True)

        # Bind events for line numbers
        self.editor.bind("<KeyRelease>", lambda e: self.update_line_numbers())
        self.editor.bind("<MouseWheel>", lambda e: self.update_line_numbers())
        self.editor.bind("<Button-4>", lambda e: self.update_line_numbers())
        self.editor.bind("<Button-5>", lambda e: self.update_line_numbers())

        # Configure error highlight tag
        self.editor.tag_configure("error", background="#FFDDDD", foreground="red")

        self.content.add(self.editor_panel, minsize=600)

    def setup_io_panel(self):
        """Create the input/output panel"""
        self.io_panel = tk.Frame(self.content, bg="#F5F5F5")

        # Output section
        self.setup_output_section()

        # Input section (hidden by default)
        self.setup_input_section()

        self.content.add(self.io_panel, minsize=600)

    def setup_output_section(self):
        """Create the output display section"""
        # Output header
        self.output_header = tk.Label(
            self.io_panel,
            text="PROGRAM OUTPUT",
            font=self.section_font,
            bg=self.header_colors["output"],
            fg="white",
            padx=10,
            pady=5
        )
        self.output_header.pack(fill="x", pady=(0, 5))

        # Output text area
        self.output = scrolledtext.ScrolledText(
            self.io_panel,
            font=self.output_font,
            state="normal",
            bg=self.io_bg,
            fg="#333333",
            padx=10,
            pady=10,
            height=15,
            insertbackground="#333333"
        )
        self.output.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        # Configure output tags for colored text
        self.output.tag_configure("error", foreground="red")
        self.output.tag_configure("warning", foreground="orange")
        self.output.tag_configure("info", foreground="blue")

    def setup_input_section(self):
        """Create the input section (hidden by default)"""
        # Input header
        self.input_header = tk.Label(
            self.io_panel,
            text="PROGRAM INPUT",
            font=self.section_font,
            bg=self.header_colors["input"],
            fg="white",
            padx=10,
            pady=5
        )

        # Input text area
        self.input_entry = tk.Text(
            self.io_panel,
            font=self.output_font,
            bg=self.io_bg,
            fg="#333333",
            insertbackground="#333333",
            height=5,
            padx=10,
            pady=10
        )

        # Submit button
        self.input_button = tk.Button(
            self.io_panel,
            text="SUBMIT INPUT",
            command=self.submit_input,
            bg=self.header_colors["input"],
            fg="white",
            font=self.button_font,
            padx=20,
            pady=5
        )

    def setup_status_bar(self):
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
            "<Control-s>": lambda e: self.save_file(),
            "<Control-o>": lambda e: self.open_file(),
            "<Control-r>": lambda e: self.run_code(),
            "<F5>": lambda e: self.debug_code(),
            "<Control-n>": lambda e: self.new_file(),
            "<Control-z>": lambda e: self.undo(),
            "<Control-y>": lambda e: self.redo(),
            "<Control-x>": lambda e: self.cut(),
            "<Control-c>": lambda e: self.copy(),
            "<Control-v>": lambda e: self.paste(),
            "<Control-a>": lambda e: self.select_all(),
            "<F1>": lambda e: self.show_help()
        }

        for key, command in shortcuts.items():
            self.root.bind(key, command)

    def clear_output(self):
        """Clear the output console"""
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.config(state="disabled")
        self.status_bar.config(text="Output cleared")

    def append_output(self, text):
        """Append text to the output console"""
        self.output.config(state="normal")
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state="disabled")

        # Check if program is waiting for input
        if "input(" in text or "input (" in text:
            self.waiting_for_input = True
            self.show_input_widgets()
            self.status_bar.config(text="Waiting for input...")
            self.input_entry.focus()

    def append_error(self, text):
        """Append formatted error text to the output console"""
        self.output.config(state="normal")

        # Insert the text with appropriate formatting
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

    def execution_finished(self, return_code):
        """Handle completion of program execution"""
        self.process = None
        if return_code == 0:
            self.status_bar.config(text="Execution completed successfully")
        else:
            self.status_bar.config(text=f"Execution failed with code {return_code}")

    def submit_input(self):
        """Submit input to the running program"""
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

        line_count = self.editor.get(1.0, tk.END).count('\n')
        for line in range(1, line_count + 2):
            self.line_numbers.insert(tk.END, f"{line}\n")

        self.line_numbers.config(state="disabled")

    def show_help(self):
        """Show help documentation"""
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

Features:
- Professional Python development environment
- Real-time output display with error highlighting
- Input handling for interactive programs
- Line numbers and error line highlighting
- Detailed error reporting with traceback
- Multi-file editing support

For Python documentation, visit: python.org
"""
        messagebox.showinfo("Help Documentation", help_text)
        webbrowser.open("https://docs.python.org/3/")

    def show_about(self):
        """Show about information"""
        about_text = """ZAYED PYTHON IDE

Version: 2.0
Developed by: [Your Name]

A professional Python development environment with:
- Advanced code editing
- Real-time debugging
- Error highlighting
- And much more!

Contact: your@email.com
"""
        messagebox.showinfo("About", about_text)


if __name__ == "__main__":
    root = tk.Tk()
    try:
        if platform.system() == "Windows":
            root.iconbitmap(default="python.ico")
        else:
            img = tk.PhotoImage(file="python.png")
            root.tk.call("wm", "iconphoto", root._w, img)
    except:
        pass

    ide = ZayedPythonIDE(root)
    root.mainloop()