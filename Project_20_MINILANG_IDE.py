import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
from collections import defaultdict
import os
from tkinter.font import Font
import platform
import webbrowser


class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.line}, {self.column})"


class MiniLangLexer:
    def __init__(self):
        self.keywords = {
            'if', 'else', 'while', 'print', 'int', 'float', 'bool', 'true', 'false'
        }
        self.token_spec = [
            ('NUMBER', r'\d+(\.\d*)?'),  # Integer or decimal number
            ('ID', r'[A-Za-z][A-Za-z0-9_]*'),  # Identifiers
            ('OP', r'[+\-*/%=<>!&|]'),  # Operators
            ('DELIMITER', r'[();,:{}]'),  # Delimiters
            ('STRING', r'"[^"]*"'),  # String literals
            ('COMMENT', r'//.*'),  # Comments
            ('NEWLINE', r'\n'),  # Line endings
            ('SKIP', r'[ \t]'),  # Skip over spaces and tabs
        ]
        self.token_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_spec)
        self.re_token = re.compile(self.token_regex)

    def tokenize(self, code):
        line_num = 1
        line_start = 0
        for mo in self.re_token.finditer(code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start

            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'ID' and value in self.keywords:
                kind = value.upper()
            elif kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind == 'SKIP' or kind == 'COMMENT':
                continue

            yield Token(kind, value, line_num, column)


class MiniLangParser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.current_token = None
        self.next_token()

    def next_token(self):
        try:
            self.current_token = self.tokens.pop(0)
        except IndexError:
            self.current_token = None

    def expect(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.next_token()
            return token
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token.type if self.current_token else 'EOF'}")

    def parse(self):
        """Parse the program"""
        return self.program()

    def program(self):
        """program : statement_list"""
        return {'type': 'program', 'body': self.statement_list()}

    def statement_list(self):
        """statement_list : statement | statement_list statement"""
        statements = []
        while self.current_token and self.current_token.type != '}':
            statements.append(self.statement())
        return statements

    def statement(self):
        """statement : declaration | assignment | if_statement | while_statement | print_statement"""
        if self.current_token.type in {'int', 'float', 'bool'}:
            return self.declaration()
        elif self.current_token.type == 'ID':
            return self.assignment()
        elif self.current_token.type == 'if':
            return self.if_statement()
        elif self.current_token.type == 'while':
            return self.while_statement()
        elif self.current_token.type == 'print':
            return self.print_statement()
        else:
            raise SyntaxError(f"Unexpected token {self.current_token.type}")

    def declaration(self):
        """declaration : type ID ('=' expression)? ';'"""
        type_token = self.expect(self.current_token.type)  # int, float, or bool
        id_token = self.expect('ID')

        node = {
            'type': 'declaration',
            'data_type': type_token.value,
            'id': id_token.value
        }

        if self.current_token and self.current_token.type == '=':
            self.expect('=')
            node['init'] = self.expression()

        self.expect(';')
        return node

    def assignment(self):
        """assignment : ID '=' expression ';'"""
        id_token = self.expect('ID')
        self.expect('=')
        expr = self.expression()
        self.expect(';')
        return {
            'type': 'assignment',
            'id': id_token.value,
            'value': expr
        }

    def expression(self):
        """Placeholder for expression parsing"""
        # This would be implemented with proper precedence handling
        return self.simple_expression()

    def simple_expression(self):
        """simple_expression : term (op term)*"""
        left = self.term()
        while self.current_token and self.current_token.type in ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=']:
            op = self.current_token
            self.next_token()
            right = self.term()
            left = {
                'type': 'binary_expression',
                'operator': op.value,
                'left': left,
                'right': right
            }
        return left

    def term(self):
        """term : NUMBER | STRING | ID | '(' expression ')'"""
        if self.current_token.type == 'NUMBER':
            token = self.expect('NUMBER')
            return {'type': 'number', 'value': token.value}
        elif self.current_token.type == 'STRING':
            token = self.expect('STRING')
            return {'type': 'string', 'value': token.value}
        elif self.current_token.type == 'ID':
            token = self.expect('ID')
            return {'type': 'identifier', 'name': token.value}
        elif self.current_token.type == '(':
            self.expect('(')
            expr = self.expression()
            self.expect(')')
            return expr
        else:
            raise SyntaxError(f"Unexpected token {self.current_token.type}")

    def if_statement(self):
        """if_statement : 'if' '(' expression ')' '{' statement_list '}' ('else' '{' statement_list '}')?"""
        self.expect('if')
        self.expect('(')
        condition = self.expression()
        self.expect(')')
        self.expect('{')
        if_body = self.statement_list()
        self.expect('}')

        node = {
            'type': 'if_statement',
            'condition': condition,
            'if_body': if_body
        }

        if self.current_token and self.current_token.type == 'else':
            self.expect('else')
            self.expect('{')
            node['else_body'] = self.statement_list()
            self.expect('}')

        return node

    def while_statement(self):
        """while_statement : 'while' '(' expression ')' '{' statement_list '}'"""
        self.expect('while')
        self.expect('(')
        condition = self.expression()
        self.expect(')')
        self.expect('{')
        body = self.statement_list()
        self.expect('}')
        return {
            'type': 'while_statement',
            'condition': condition,
            'body': body
        }

    def print_statement(self):
        """print_statement : 'print' '(' expression ')' ';'"""
        self.expect('print')
        self.expect('(')
        expr = self.expression()
        self.expect(')')
        self.expect(';')
        return {
            'type': 'print_statement',
            'expression': expr
        }


class SymbolTable:
    def __init__(self):
        self.symbols = defaultdict(dict)
        self.scope_level = 0

    def enter_scope(self):
        self.scope_level += 1

    def exit_scope(self):
        self.scope_level -= 1
        # Remove symbols from the current scope
        for name in list(self.symbols.keys()):
            if self.scope_level in self.symbols[name]:
                del self.symbols[name][self.scope_level]
                if not self.symbols[name]:
                    del self.symbols[name]

    def add_symbol(self, name, symbol_type, value=None):
        self.symbols[name][self.scope_level] = {
            'type': symbol_type,
            'value': value
        }

    def lookup(self, name):
        for level in range(self.scope_level, -1, -1):
            if name in self.symbols and level in self.symbols[name]:
                return self.symbols[name][level]
        return None


class MiniLangIDE:
    def __init__(self, root):
        # Set up the main window
        self.root = root
        self.root.title("ZAYED MINILANG IDE")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)

        # Track the current file and unsaved changes
        self.current_file = None
        self.unsaved_changes = False

        # Set up colors and fonts
        self.setup_appearance()

        # Initialize compiler components
        self.lexer = MiniLangLexer()
        self.symbol_table = SymbolTable()

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

        # Create the editor and visualization panels
        self.create_editor_panel()
        self.create_visualization_panel()

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
        """Create the title header"""
        header = tk.Frame(self.main_frame, bg="#F5F5F5")
        header.pack(fill="x", pady=(10, 15))

        # Main title
        title = tk.Label(
            header,
            text="ZAYED MINILANG IDE",
            font=self.title_font,
            fg=self.header_colors["editor"],
            bg="#F5F5F5"
        )
        title.pack(expand=True)

        # Subtitle
        subtitle = tk.Label(
            header,
            text="Compiler Development Environment",
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

        # Compile menu
        compile_menu = tk.Menu(menubar, tearoff=0)
        compile_menu.add_command(label="Compile", command=self.compile, accelerator="F5")
        compile_menu.add_command(label="Step Through", command=self.step_through)
        compile_menu.add_command(label="Run", command=self.run)
        menubar.add_cascade(label="Compile", menu=compile_menu)

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

        # Compilation buttons
        self.create_toolbar_button(toolbar, "Compile", self.compile, "#4CAF50", button_style)
        self.create_toolbar_button(toolbar, "Step", self.step_through, "#FF9800", button_style)
        self.create_toolbar_button(toolbar, "Run", self.run, "#4CAF50", button_style)
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
            text="MINILANG CODE EDITOR",
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

        # Add sample MiniLang code
        sample_code = """// MiniLang Sample Program
int x = 10;
float y = 3.14;
bool flag = true;

if (x > 5) {
    print("x is greater than 5");
} else {
    print("x is 5 or less");
}

while (x > 0) {
    print(x);
    x = x - 1;
}
"""
        self.editor.insert(tk.END, sample_code)
        self.update_line_numbers()

        self.panes.add(editor_frame, minsize=600)

    def create_visualization_panel(self):
        """Create the visualization panel with tabs"""
        visualization_frame = tk.Frame(self.panes, bg="#F5F5F5")

        # Visualization header
        visualization_header = tk.Label(
            visualization_frame,
            text="COMPILER VISUALIZATION",
            font=self.section_font,
            bg=self.header_colors["output"],
            fg="white",
            padx=10,
            pady=5
        )
        visualization_header.pack(fill="x", pady=(0, 5))

        # Notebook for tabs
        self.notebook = ttk.Notebook(visualization_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        # Create tabs for each visualization
        self.create_token_tab()
        self.create_parse_tree_tab()
        self.create_symbol_table_tab()
        self.create_tac_tab()
        self.create_output_tab()

        self.panes.add(visualization_frame, minsize=600)

    def create_token_tab(self):
        """Create the token stream tab with framed box"""
        self.token_tab = ttk.Frame(self.notebook)

        # Create a frame with border
        token_frame = ttk.Frame(self.token_tab, borderwidth=2, relief="groove")
        token_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.token_text = scrolledtext.ScrolledText(
            token_frame,
            state="disabled",
            font=self.output_font,
            bg=self.io_bg,
            padx=10,
            pady=10
        )
        self.token_text.pack(fill="both", expand=True)
        self.notebook.add(self.token_tab, text="Token Stream")

    def create_parse_tree_tab(self):
        """Create the parse tree tab with framed box"""
        self.parse_tree_tab = ttk.Frame(self.notebook)

        # Create a frame with border
        parse_tree_frame = ttk.Frame(self.parse_tree_tab, borderwidth=2, relief="groove")
        parse_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.parse_tree_text = scrolledtext.ScrolledText(
            parse_tree_frame,
            state="disabled",
            font=self.output_font,
            bg=self.io_bg,
            padx=10,
            pady=10
        )
        self.parse_tree_text.pack(fill="both", expand=True)
        self.notebook.add(self.parse_tree_tab, text="Parse Tree")

    def create_symbol_table_tab(self):
        """Create the symbol table tab with framed box"""
        self.symbol_table_tab = ttk.Frame(self.notebook)

        # Create a frame with border
        symbol_table_frame = ttk.Frame(self.symbol_table_tab, borderwidth=2, relief="groove")
        symbol_table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.symbol_table_text = scrolledtext.ScrolledText(
            symbol_table_frame,
            state="disabled",
            font=self.output_font,
            bg=self.io_bg,
            padx=10,
            pady=10
        )
        self.symbol_table_text.pack(fill="both", expand=True)
        self.notebook.add(self.symbol_table_tab, text="Symbol Table")

    def create_tac_tab(self):
        """Create the three address code tab with framed box"""
        self.tac_tab = ttk.Frame(self.notebook)

        # Create a frame with border
        tac_frame = ttk.Frame(self.tac_tab, borderwidth=2, relief="groove")
        tac_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.tac_text = scrolledtext.ScrolledText(
            tac_frame,
            state="disabled",
            font=self.output_font,
            bg=self.io_bg,
            padx=10,
            pady=10
        )
        self.tac_text.pack(fill="both", expand=True)
        self.notebook.add(self.tac_tab, text="Three Address Code")

    def create_output_tab(self):
        """Create the output tab with framed box"""
        self.output_tab = ttk.Frame(self.notebook)

        # Create a frame with border
        output_frame = ttk.Frame(self.output_tab, borderwidth=2, relief="groove")
        output_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            state="normal",
            font=self.output_font,
            bg=self.io_bg,
            padx=10,
            pady=10
        )
        self.output_text.pack(fill="both", expand=True)
        self.notebook.add(self.output_tab, text="VM Output")

    def create_status_bar(self):
        """Create the status bar at bottom"""
        self.status_bar = tk.Label(
            self.main_frame,
            text="Ready | Zayed MiniLang IDE | Ctrl+S to Save | F5 to Compile",
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
            "<F5>": self.compile,
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
        self.root.title("ZAYED MINILANG IDE")
        self.status_bar.config(text="New file created")
        self.update_line_numbers()

    def open_file(self):
        """Open an existing MiniLang file"""
        if self.unsaved_changes:
            if not messagebox.askyesno("Unsaved Changes", "Save current file first?"):
                return
            self.save_file()

        file_path = filedialog.askopenfilename(filetypes=[("MiniLang Files", "*.ml"), ("All Files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, file.read())

            self.current_file = file_path
            self.unsaved_changes = False
            self.root.title(f"{os.path.basename(file_path)} - ZAYED MINILANG IDE")
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
                self.root.title(f"{os.path.basename(self.current_file)} - ZAYED MINILANG IDE")
                self.status_bar.config(text=f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save with a new filename"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ml",
            filetypes=[("MiniLang Files", "*.ml"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w") as file:
                file.write(self.editor.get("1.0", tk.END))

            self.current_file = file_path
            self.unsaved_changes = False
            self.root.title(f"{os.path.basename(file_path)} - ZAYED MINILANG IDE")
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

    # Compilation functions
    def compile(self):
        """Compile the current MiniLang code"""
        code = self.editor.get("1.0", tk.END)

        # Clear any existing error highlights
        self.editor.tag_remove("error", "1.0", "end")

        try:
            # Clear all visualization tabs first
            self.clear_visualizations()

            # Lexical Analysis
            tokens = list(self.lexer.tokenize(code))
            self.show_token_stream(tokens)

            # Syntax Analysis
            parser = MiniLangParser(tokens)
            parse_tree = parser.parse()
            self.show_parse_tree(parse_tree)

            # Semantic Analysis
            self.analyze_semantics(parse_tree)
            self.show_symbol_table()

            # Generate TAC
            tac = self.generate_tac(parse_tree)
            self.show_tac(tac)

            self.status_bar.config(text="Compilation successful")
            self.append_output("Compilation successful!\n")

        except Exception as e:
            error_msg = str(e)
            self.status_bar.config(text=f"Compilation error: {error_msg}")
            self.append_output(f"Compilation error: {error_msg}\n")

            # Try to highlight error line
            line_number = self.find_error_line(error_msg)
            if line_number:
                self.highlight_error_line(line_number)

    def clear_visualizations(self):
        """Clear all visualization tabs"""
        self.token_text.config(state="normal")
        self.token_text.delete("1.0", tk.END)
        self.token_text.config(state="disabled")

        self.parse_tree_text.config(state="normal")
        self.parse_tree_text.delete("1.0", tk.END)
        self.parse_tree_text.config(state="disabled")

        self.symbol_table_text.config(state="normal")
        self.symbol_table_text.delete("1.0", tk.END)
        self.symbol_table_text.config(state="disabled")

        self.tac_text.config(state="normal")
        self.tac_text.delete("1.0", tk.END)
        self.tac_text.config(state="disabled")

        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state="disabled")

    def show_token_stream(self, tokens):
        """Display token stream in the token tab"""
        self.token_text.config(state="normal")
        self.token_text.delete("1.0", tk.END)

        # Add header
        self.token_text.insert(tk.END, "TOKEN STREAM\n")
        self.token_text.insert(tk.END, "=" * 50 + "\n\n")

        # Add column headers
        self.token_text.insert(tk.END, f"{'Type':<15} {'Value':<20} {'Line':<5} {'Column':<5}\n")
        self.token_text.insert(tk.END, "-" * 50 + "\n")

        for token in tokens:
            self.token_text.insert(tk.END,
                                   f"{token.type:<15} {str(token.value):<20} {token.line:<5} {token.column:<5}\n")

        self.token_text.config(state="disabled")

    def show_parse_tree(self, parse_tree):
        """Display parse tree in the parse tree tab"""
        self.parse_tree_text.config(state="normal")
        self.parse_tree_text.delete("1.0", tk.END)

        # Add header
        self.parse_tree_text.insert(tk.END, "PARSE TREE\n")
        self.parse_tree_text.insert(tk.END, "=" * 50 + "\n\n")

        def print_tree(node, level=0):
            indent = "  " * level
            if isinstance(node, dict):
                result = indent + node.get('type', 'node') + ":\n"
                for key, value in node.items():
                    if key != 'type':
                        result += indent + f"  {key}: "
                        if isinstance(value, (dict, list)):
                            result += "\n" + print_tree(value, level + 2)
                        else:
                            result += str(value) + "\n"
                return result
            elif isinstance(node, list):
                result = ""
                for item in node:
                    result += print_tree(item, level)
                return result
            else:
                return indent + str(node) + "\n"

        self.parse_tree_text.insert(tk.END, print_tree(parse_tree))
        self.parse_tree_text.config(state="disabled")

    def analyze_semantics(self, parse_tree):
        """Perform semantic analysis and populate symbol table"""
        self.symbol_table = SymbolTable()  # Reset symbol table

        def analyze_node(node):
            if node['type'] == 'declaration':
                self.symbol_table.add_symbol(
                    node['id'],
                    node['data_type'],
                    node.get('init', None)
                )
            # Additional semantic checks would go here

        if parse_tree['type'] == 'program':
            for stmt in parse_tree['body']:
                analyze_node(stmt)

    def show_symbol_table(self):
        """Display symbol table in the symbol table tab"""
        self.symbol_table_text.config(state="normal")
        self.symbol_table_text.delete("1.0", tk.END)

        # Add header
        self.symbol_table_text.insert(tk.END, "SYMBOL TABLE\n")
        self.symbol_table_text.insert(tk.END, "=" * 50 + "\n\n")

        # Add column headers
        self.symbol_table_text.insert(tk.END, f"{'Name':<15} {'Scope':<10} {'Type':<10} {'Value':<15}\n")
        self.symbol_table_text.insert(tk.END, "-" * 50 + "\n")

        for name in self.symbol_table.symbols:
            for level in self.symbol_table.symbols[name]:
                symbol = self.symbol_table.symbols[name][level]
                self.symbol_table_text.insert(
                    tk.END,
                    f"{name:<15} {level:<10} {symbol['type']:<10} {str(symbol.get('value', '')):<15}\n"
                )

        self.symbol_table_text.config(state="disabled")

    def generate_tac(self, parse_tree):
        """Generate Three Address Code from parse tree"""
        tac = []

        def generate_from_node(node):
            if node['type'] == 'declaration':
                if 'init' in node:
                    temp = f"t{len(tac)}"
                    tac.append(f"{temp} = {self.format_value(node['init'])}")
                    tac.append(f"{node['id']} = {temp}")
                else:
                    tac.append(f"{node['id']} = ?")
            elif node['type'] == 'assignment':
                temp = f"t{len(tac)}"
                tac.append(f"{temp} = {self.format_value(node['value'])}")
                tac.append(f"{node['id']} = {temp}")
            elif node['type'] == 'print_statement':
                tac.append(f"print {self.format_value(node['expression'])}")
            elif node['type'] == 'if_statement':
                condition = self.format_value(node['condition'])
                tac.append(f"if {condition} goto L{len(tac)+1}")
                tac.append("goto Lendif")
                tac.append(f"L{len(tac)-1}:")
                for stmt in node['if_body']:
                    generate_from_node(stmt)
                if 'else_body' in node:
                    tac.append("goto Lendelse")
                    tac.append("Lendif:")
                    for stmt in node['else_body']:
                        generate_from_node(stmt)
                    tac.append("Lendelse:")
                else:
                    tac.append("Lendif:")
            elif node['type'] == 'while_statement':
                tac.append(f"Lwhile{len(tac)}:")
                condition = self.format_value(node['condition'])
                tac.append(f"if {condition} goto L{len(tac)+1}")
                tac.append("goto Lendwhile")
                tac.append(f"L{len(tac)-1}:")
                for stmt in node['body']:
                    generate_from_node(stmt)
                tac.append(f"goto Lwhile{len(tac)-3}")
                tac.append("Lendwhile:")

        if parse_tree['type'] == 'program':
            for stmt in parse_tree['body']:
                generate_from_node(stmt)

        return tac

    def format_value(self, node):
        """Format a value node for TAC display"""
        if isinstance(node, dict):
            if node['type'] == 'number':
                return str(node['value'])
            elif node['type'] == 'string':
                return node['value']
            elif node['type'] == 'identifier':
                return node['name']
            elif node['type'] == 'binary_expression':
                left = self.format_value(node['left'])
                right = self.format_value(node['right'])
                return f"{left} {node['operator']} {right}"
        return str(node)

    def show_tac(self, tac):
        """Display three address code in the TAC tab"""
        self.tac_text.config(state="normal")
        self.tac_text.delete("1.0", tk.END)

        # Add header
        self.tac_text.insert(tk.END, "THREE ADDRESS CODE\n")
        self.tac_text.insert(tk.END, "="*50 + "\n\n")

        for i, instruction in enumerate(tac):
            self.tac_text.insert(tk.END, f"{i:>3}: {instruction}\n")

        self.tac_text.config(state="disabled")

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

    def step_through(self):
        """Step through compilation phases"""
        # TODO: Implement step-through functionality
        self.status_bar.config(text="Step-through not yet implemented")
        messagebox.showinfo("Info", "Step-through functionality will be implemented in a future version")

    def run(self):
        """Run the compiled code"""
        # TODO: Implement VM execution
        self.status_bar.config(text="VM execution not yet implemented")
        messagebox.showinfo("Info", "Virtual Machine execution will be implemented in a future version")

    def clear_output(self):
        """Clear the output panel"""
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state="disabled")
        self.status_bar.config(text="Output cleared")

    def append_output(self, text):
        """Add text to the output panel"""
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")

    # Help and about
    def show_help(self):
        """Show help information"""
        help_text = """ZAYED MINILANG IDE - HELP

Shortcuts:
Ctrl+N - New File
Ctrl+O - Open File
Ctrl+S - Save File
F5 - Compile Code
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+X - Cut
Ctrl+C - Copy
Ctrl+V - Paste
Ctrl+A - Select All
F1 - Show Help

For MiniLang documentation, visit: example.com/minilang
"""
        messagebox.showinfo("Help", help_text)
        webbrowser.open("https://example.com/minilang")

    def show_about(self):
        """Show about dialog"""
        about_text = """ZAYED MINILANG IDE

Version: 2.0
Developed by: Hossain Mohammad Jayed

A professional MiniLang development environment.
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
    ide = MiniLangIDE(root)
    root.mainloop()