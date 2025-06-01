import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, PhotoImage
import json
from datetime import datetime
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os


class ModernTodoList:
    def __init__(self, root):
        self.root = root
        self.root.title("JB ToDo List")
        self.root.geometry("850x750")
        self.root.configure(bg="#ffffff")

        # Logo Path
        self.logo_path = "../images/jbtodolist.png"  # Change this to your actual logo path
        self.logo_image = None

        self._create_menu_bar()

        self.status_var = tk.StringVar()
        self.tasks = []
        self.filtered_tasks = []
        self.load_tasks()

        self.style = ttk.Style()
        self.style.theme_use('clam')

        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Header Frame with Logo and Title
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 15), fill=tk.X)

        self.logo_label = ttk.Label(header_frame)
        self.logo_label.pack(side=tk.LEFT, padx=(0, 10), anchor='nw')
        self._load_and_display_logo()

        title_label = ttk.Label(header_frame, text="JB ToDo List", font=("Segoe UI", 26, "bold"), foreground="#fd7e14")
        title_label.pack(side=tk.LEFT, anchor='w')

        # Input Frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.task_entry = ttk.Entry(input_frame, font=("Segoe UI", 12), width=40)
        self.task_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5, padx=(0, 10))
        self.task_entry.insert(0, "Enter task description...")
        self.task_entry.configure(foreground="#aaaaaa")
        self.task_entry.bind("<FocusIn>", self.clear_placeholder_entry)
        self.task_entry.bind("<FocusOut>", self.add_placeholder_entry)
        self.task_entry.bind("<Return>", self.add_task_event)

        # Details Frame
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.X, pady=(0, 10))

        priority_label = ttk.Label(details_frame, text="Priority:")
        priority_label.pack(side=tk.LEFT, padx=(0, 5), pady=(5, 0))
        self.priority_var = tk.StringVar(value="Medium")
        priority_options = ["High", "Medium", "Low"]
        self.priority_combobox = ttk.Combobox(details_frame, textvariable=self.priority_var,
                                              values=priority_options, state="readonly", width=10,
                                              font=("Segoe UI", 10))
        self.priority_combobox.pack(side=tk.LEFT, padx=(0, 20), pady=(5, 0))

        due_date_label = ttk.Label(details_frame, text="Due Date (YYYY-MM-DD):")
        due_date_label.pack(side=tk.LEFT, padx=(0, 5), pady=(5, 0))
        self.due_date_entry = ttk.Entry(details_frame, font=("Segoe UI", 10), width=15)
        self.due_date_entry.pack(side=tk.LEFT, ipady=2, pady=(5, 0), padx=(0, 20))
        self.due_date_entry.insert(0, "Optional")
        self.due_date_entry.configure(foreground="#aaaaaa")
        self.due_date_entry.bind("<FocusIn>", lambda e: self.clear_placeholder_date(e, "Optional"))
        self.due_date_entry.bind("<FocusOut>", lambda e: self.add_placeholder_date(e, "Optional"))

        self.add_button = ttk.Button(details_frame, text="🚀 Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, ipady=4, pady=(5, 0))

        # Filter and Sort Frame
        filter_sort_frame = ttk.Frame(main_frame)
        filter_sort_frame.pack(fill=tk.X, pady=(15, 10))

        filter_label = ttk.Label(filter_sort_frame, text="Filter by Status:")
        filter_label.pack(side=tk.LEFT, padx=(0, 5))
        self.filter_var = tk.StringVar(value="All")
        filter_options = ["All", "Pending", "Completed"]
        self.filter_combobox = ttk.Combobox(filter_sort_frame, textvariable=self.filter_var,
                                            values=filter_options, state="readonly", width=12,
                                            font=("Segoe UI", 10))
        self.filter_combobox.pack(side=tk.LEFT, padx=(0, 20))
        self.filter_combobox.bind("<<ComboboxSelected>>", self.filter_tasks)

        sort_label = ttk.Label(filter_sort_frame, text="Sort by:")
        sort_label.pack(side=tk.LEFT, padx=(0, 5))
        self.sort_var = tk.StringVar(value="Default")
        sort_options = ["Default", "Priority (High-Low)", "Due Date (Soonest)", "Description (A-Z)"]
        self.sort_combobox = ttk.Combobox(filter_sort_frame, textvariable=self.sort_var,
                                          values=sort_options, state="readonly", width=20,
                                          font=("Segoe UI", 10))
        self.sort_combobox.pack(side=tk.LEFT, padx=(0, 10))
        self.sort_combobox.bind("<<ComboboxSelected>>", self.sort_tasks)

        # Task Tree Frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 10))

        self.task_tree = ttk.Treeview(tree_frame,
                                      columns=("ID", "Description", "Priority", "Due Date", "Status", "Added"),
                                      show="headings", selectmode="extended")
        self.task_tree.heading("ID", text="ID", anchor=tk.W)
        self.task_tree.heading("Description", text="Description", anchor=tk.W)
        self.task_tree.heading("Priority", text="Priority", anchor=tk.CENTER)
        self.task_tree.heading("Due Date", text="Due Date", anchor=tk.CENTER)
        self.task_tree.heading("Status", text="Status", anchor=tk.CENTER)
        self.task_tree.heading("Added", text="Date Added", anchor=tk.CENTER)

        self.task_tree.column("ID", width=40, stretch=tk.NO, anchor=tk.W)
        self.task_tree.column("Description", width=300, anchor=tk.W)
        self.task_tree.column("Priority", width=80, anchor=tk.CENTER)
        self.task_tree.column("Due Date", width=100, anchor=tk.CENTER)
        self.task_tree.column("Status", width=100, anchor=tk.CENTER)
        self.task_tree.column("Added", width=120, anchor=tk.CENTER)
        self.task_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.task_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        # Apply styles after creating all widgets
        self._apply_light_theme_styles()

        # Action Buttons Frame
        action_buttons_frame = ttk.Frame(main_frame)
        action_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        self.complete_button = ttk.Button(action_buttons_frame, text="✅ Mark Complete/Pending",
                                          command=self.mark_complete)
        self.complete_button.pack(side=tk.LEFT, padx=(0, 10), ipady=4)
        self.edit_button = ttk.Button(action_buttons_frame, text="✏️ Edit Task", command=self.edit_task)
        self.edit_button.pack(side=tk.LEFT, padx=(0, 10), ipady=4)
        self.delete_button = ttk.Button(action_buttons_frame, text="❌ Delete Task", command=self.delete_task)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 10), ipady=4)
        self.clear_all_button = ttk.Button(action_buttons_frame, text="🗑️ Clear All Tasks",
                                           command=self.clear_all_tasks_ui)
        self.clear_all_button.pack(side=tk.RIGHT, ipady=4)

        # Status Bar
        status_bar = ttk.Label(root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        if not self.tasks:
            self.status_var.set("Welcome to JB ToDo List! Add some tasks.")
        self.refresh_task_list()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _apply_light_theme_styles(self):
        self.style.configure("TFrame", background="#ffffff")
        self.style.configure("TLabel", background="#ffffff", foreground="#333333", font=("Segoe UI", 11))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#007bff")
        self.style.map("TButton",
                       background=[('active', '#0056b3'), ('disabled', '#c0c0c0')],
                       foreground=[('disabled', '#777777')])

        self.style.configure("Treeview", background="#ffffff", foreground="#333333",
                             fieldbackground="#ffffff", rowheight=30, font=("Segoe UI", 10))
        self.style.map("Treeview",
                       background=[('selected', '#cce5ff')],
                       foreground=[('selected', '#004085')])
        self.style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"),
                             background="#e9ecef", foreground="#495057")
        self.style.map("Treeview.Heading", background=[('active', '#d6d8db')])

        self.style.configure("TCombobox", font=("Segoe UI", 10), fieldbackground="#ffffff",
                             background="#e9ecef", foreground="#495057", arrowcolor="#495057")
        self.root.option_add('*TCombobox*Listbox.background', '#ffffff')
        self.root.option_add('*TCombobox*Listbox.foreground', '#495057')
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#007bff')
        self.root.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')

        self.style.configure("Vertical.TScrollbar", background="#007bff", troughcolor="#e9ecef",
                             bordercolor="#e9ecef", arrowcolor="#ffffff")
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"),
                             foreground="#ffffff", background="#28a745")
        self.style.map("Accent.TButton", background=[('active', '#1e7e34')])
        self.style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"),
                             foreground="#ffffff", background="#dc3545")
        self.style.map("Danger.TButton", background=[('active', '#bd2130')])
        self.style.configure("Status.TLabel", background="#e9ecef", foreground="#495057",
                             relief=tk.SUNKEN, font=("Segoe UI", 9), padding=3)

        # Configure Treeview tags
        self.task_tree.tag_configure('completed', foreground='#6c757d', font=("Segoe UI", 10, "overstrike"))
        self.task_tree.tag_configure('pending', foreground='#333333')
        self.task_tree.tag_configure('due_soon', background='#fff3cd', foreground='#856404')
        self.task_tree.tag_configure('overdue', background='#f8d7da', foreground='#721c24')

    def _load_and_display_logo(self):
        try:
            if not os.path.exists(self.logo_path) or self.logo_path == "path/to/your/logo.png":
                img = Image.new('RGB', (150, 50), color=(220, 220, 220))
                self.status_var.set("Logo not found or path not set. Displaying placeholder.")
            else:
                img = Image.open(self.logo_path)

            img.thumbnail((150, 70))
            self.logo_image = ImageTk.PhotoImage(img)
            self.logo_label.config(image=self.logo_image)
            self.logo_label.image = self.logo_image
        except Exception as e:
            self.status_var.set(f"Error loading logo: {e}")
            self.logo_label.config(text="[Logo Error]", font=("Segoe UI", 10))

    def _create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New List", command=self._new_list_confirmation)
        file_menu.add_separator()
        file_menu.add_command(label="Save (JSON)", command=self.save_tasks)
        file_menu.add_command(label="Save As PDF...", command=self._save_as_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self._show_user_guide)
        help_menu.add_command(label="About JB ToDo List", command=self._show_about_us)

    def _new_list_confirmation(self):
        if messagebox.askyesno("New List",
                               "Are you sure you want to create a new list? All current unsaved tasks will be lost.",
                               parent=self.root):
            self.tasks = []
            self.refresh_task_list()
            self.save_tasks()
            self.status_var.set("New list created. Previous tasks cleared.")

    def clear_all_tasks_ui(self):
        if not self.tasks:
            messagebox.showinfo("No Tasks", "There are no tasks to clear.", parent=self.root)
            return
        if messagebox.askyesno("Confirm Clear All", "Are you sure you want to delete ALL tasks? This cannot be undone.",
                               parent=self.root, icon='warning'):
            self.tasks = []
            self.refresh_task_list()
            self.save_tasks()
            self.status_var.set("All tasks cleared.")

    def _save_as_pdf(self):
        if not self.tasks:
            messagebox.showinfo("No Tasks", "There are no tasks to export to PDF.", parent=self.root)
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")],
            title="Save To-Do List as PDF",
            initialfile="JB_ToDo_List.pdf"
        )

        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = styles['h1']
            title_style.alignment = 1
            story.append(Paragraph("JB ToDo List", title_style))
            story.append(Spacer(1, 0.25 * 72))

            # Date
            date_style = styles['Normal']
            date_style.alignment = 2
            story.append(Paragraph(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
            story.append(Spacer(1, 0.25 * 72))

            # Table Data
            data = [["ID", "Description", "Priority", "Due Date", "Status", "Added On"]]
            tasks_for_pdf = []
            for child_iid in self.task_tree.get_children():
                item = self.task_tree.item(child_iid)
                values = item['values']
                tasks_for_pdf.append(values)

            for task_values in tasks_for_pdf:
                data.append([str(v) if v is not None else "N/A" for v in task_values])

            if len(data) == 1:
                story.append(Paragraph("No tasks to display in the current view.", styles['Normal']))
            else:
                table = Table(data, colWidths=[30, 220, 60, 70, 70, 90])
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (1, 1), (1, -1), 5),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ])
                table.setStyle(table_style)
                story.append(table)

            doc.build(story)
            messagebox.showinfo("PDF Saved", f"To-Do list saved as PDF:\n{file_path}", parent=self.root)
            self.status_var.set(f"List saved to PDF: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to save PDF: {e}", parent=self.root)
            self.status_var.set(f"Error saving PDF.")

    def _show_about_us(self):
        about_text = """JB ToDo List
Version 1.1

Created with Python and Tkinter.
A modern and bright way to manage your tasks!

Developed by: [Your Name/Organization Here]"""
        messagebox.showinfo("About JB ToDo List", about_text, parent=self.root)

    def _show_user_guide(self):
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide - JB ToDo List")
        guide_window.geometry("700x550")
        guide_window.configure(bg="#ffffff")
        guide_window.transient(self.root)
        guide_window.grab_set()

        text_frame = ttk.Frame(guide_window, padding=10)
        text_frame.pack(expand=True, fill=tk.BOTH)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Segoe UI", 10),
                              relief=tk.FLAT, bg="#ffffff", fg="#333333", padx=10, pady=10)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(expand=True, fill=tk.BOTH)

        guide_content = """Welcome to the JB ToDo List User Guide!

**1. Main Interface Overview:**
   - **Logo & Title:** Displays the application logo and name.
   - **Task Input:** Field to enter task description, priority, and due date.
   - **Add Task Button (🚀):** Adds the entered task to the list.
   - **Filter & Sort:** Dropdowns to filter tasks by status and sort them.
   - **Task List (Treeview):** Displays your tasks with columns for ID, Description, Priority, Due Date, Status, and Date Added.
     - *Pending tasks* are shown normally.
     - *Completed tasks* are struck-through and grayed out.
     - *Tasks due soon* are highlighted in light yellow.
     - *Overdue tasks* are highlighted in light red.
   - **Action Buttons:**
     - **✅ Mark Complete/Pending:** Toggles the status of selected task(s).
     - **✏️ Edit Task:** Opens a dialog to modify the selected task's details.
     - **❌ Delete Task:** Deletes selected task(s) after confirmation.
     - **🗑️ Clear All Tasks:** Deletes ALL tasks after confirmation.
   - **Status Bar:** Shows messages about recent actions or task counts.

**2. Adding a Task:**
   1. Type the task description.
   2. Select a Priority (High, Medium, Low).
   3. Optionally, enter a Due Date in YYYY-MM-DD format.
   4. Click the "🚀 Add Task" button or press Enter.

**3. Managing Tasks:**
   - **Selecting Tasks:** Click on a task to select it. Hold Ctrl to select multiple tasks.
   - **Marking Complete/Pending:** Select task(s) and click "✅ Mark Complete/Pending".
   - **Editing a Task:** Select ONE task and click "✏️ Edit Task".
   - **Deleting Task(s):** Select task(s) and click "❌ Delete Task".

**4. Filtering and Sorting:**
   - **Filter by Status:** View All, Pending, or Completed tasks.
   - **Sort by:** Arrange tasks by Default, Priority, Due Date, or Description.

**5. Menu Bar:**
   - **File Menu:**
     - **New List:** Clears all current tasks.
     - **Save (JSON):** Saves your current task list.
     - **Save As PDF...:** Exports tasks to a PDF file.
     - **Exit:** Closes the application.
   - **Help Menu:**
     - **User Guide:** Shows this help window.
     - **About JB ToDo List:** Displays application information.

**6. Data Storage:**
   - Your tasks are automatically saved in `todolist_data.json`.
   - When you open the application, it loads tasks from this file.

We hope you enjoy using JB ToDo List!"""
        text_widget.insert(tk.END, guide_content)
        text_widget.config(state=tk.DISABLED)

        close_button = ttk.Button(guide_window, text="Close Guide", command=guide_window.destroy)
        close_button.pack(pady=10)

    def clear_placeholder_entry(self, event):
        if self.task_entry.get() == "Enter task description...":
            self.task_entry.delete(0, tk.END)
            self.task_entry.configure(foreground="#333333")

    def add_placeholder_entry(self, event):
        if not self.task_entry.get():
            self.task_entry.insert(0, "Enter task description...")
            self.task_entry.configure(foreground="#aaaaaa")

    def clear_placeholder_date(self, event, placeholder):
        entry_widget = event.widget
        if entry_widget.get() == placeholder:
            entry_widget.delete(0, tk.END)
            entry_widget.configure(foreground="#333333")

    def add_placeholder_date(self, event, placeholder):
        entry_widget = event.widget
        if not entry_widget.get():
            entry_widget.insert(0, placeholder)
            entry_widget.configure(foreground="#aaaaaa")

    def add_task_event(self, event=None):
        self.add_task()

    def add_task(self):
        description = self.task_entry.get().strip()
        priority = self.priority_var.get()
        due_date_str = self.due_date_entry.get().strip()

        if not description or description == "Enter task description...":
            messagebox.showwarning("Input Error", "Task description cannot be empty.", parent=self.root)
            return

        valid_due_date = None
        if due_date_str and due_date_str != "Optional":
            try:
                datetime.strptime(due_date_str, "%Y-%m-%d")
                valid_due_date = due_date_str
            except ValueError:
                messagebox.showwarning("Input Error", "Invalid due date format. Please use YYYY-MM-DD.",
                                       parent=self.root)
                return
        elif due_date_str == "Optional":
            valid_due_date = None

        max_id = max(task.get('id', 0) for task in self.tasks) if self.tasks else 0
        task_id = max_id + 1

        task = {
            "id": task_id,
            "description": description,
            "priority": priority,
            "due_date": valid_due_date,
            "status": "Pending",
            "added_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.tasks.append(task)
        self.task_entry.delete(0, tk.END)
        self.add_placeholder_entry(None)
        self.due_date_entry.delete(0, tk.END)
        self.add_placeholder_date(type('event', (object,), {'widget': self.due_date_entry})(), "Optional")
        self.priority_var.set("Medium")
        self.refresh_task_list()
        self.save_tasks()
        self.status_var.set(f"Task '{description[:30]}...' added!")
        self.task_entry.focus_set()

    def get_task_display_values(self, task):
        due_date_display = task.get('due_date') if task.get('due_date') else "N/A"
        return (task['id'], task['description'], task['priority'], due_date_display, task['status'], task['added_date'])

    def refresh_task_list(self):
        self.filter_tasks()

    def filter_tasks(self, event=None):
        filter_value = self.filter_var.get()
        current_tasks = list(self.tasks)

        if filter_value == "Pending":
            self.filtered_tasks = [task for task in current_tasks if task['status'] == "Pending"]
        elif filter_value == "Completed":
            self.filtered_tasks = [task for task in current_tasks if task['status'] == "Completed"]
        else:
            self.filtered_tasks = current_tasks

        self.sort_tasks()

    def sort_tasks(self, event=None):
        sort_value = self.sort_var.get()
        tasks_to_display = list(self.filtered_tasks)

        if sort_value == "Priority (High-Low)":
            priority_map = {"High": 1, "Medium": 2, "Low": 3, None: 4}
            tasks_to_display.sort(key=lambda task: (priority_map.get(task.get('priority'), 4), task.get('id')))
        elif sort_value == "Due Date (Soonest)":
            tasks_to_display.sort(key=lambda task: (
                datetime.strptime(task['due_date'], "%Y-%m-%d") if task.get('due_date')
                else datetime.max, task.get('id')))
        elif sort_value == "Description (A-Z)":
            tasks_to_display.sort(key=lambda task: (task['description'].lower(), task.get('id')))
        else:
            tasks_to_display.sort(key=lambda task: task.get('id', 0))

        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        for task in tasks_to_display:
            values = self.get_task_display_values(task)
            tags = []

            if task['status'] == 'Completed':
                tags.append('completed')
            else:
                tags.append('pending')
                if task.get('due_date'):
                    try:
                        due_date_obj = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
                        today = datetime.now().date()
                        delta = (due_date_obj - today).days
                        if delta < 0:
                            tags.append('overdue')
                        elif 0 <= delta <= 2:
                            tags.append('due_soon')
                    except (ValueError, TypeError):
                        pass

            self.task_tree.insert("", tk.END, values=values, iid=str(task['id']), tags=tuple(tags))

        self.status_var.set(f"{len(tasks_to_display)} tasks displayed.")

    def mark_complete(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Error", "Please select a task to mark.", parent=self.root)
            return

        updated_count = 0
        for item_iid_str in selected_items:
            try:
                task_id = int(item_iid_str)
            except ValueError:
                continue

            for task in self.tasks:
                if task['id'] == task_id:
                    task['status'] = "Completed" if task['status'] == "Pending" else "Pending"
                    self.status_var.set(f"Task '{task['description'][:30]}...' marked {task['status'].lower()}.")
                    updated_count += 1
                    break

        if updated_count > 0:
            self.refresh_task_list()
            self.save_tasks()
        if updated_count > 1:
            self.status_var.set(f"{updated_count} tasks updated.")

    def edit_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Error", "Please select a task to edit.", parent=self.root)
            return
        if len(selected_items) > 1:
            messagebox.showwarning("Selection Error", "Please select only one task to edit.", parent=self.root)
            return

        try:
            task_id = int(selected_items[0])
        except ValueError:
            messagebox.showerror("Error", "Invalid task ID.", parent=self.root)
            return

        task_to_edit = next((t for t in self.tasks if t['id'] == task_id), None)
        if not task_to_edit:
            messagebox.showerror("Error", "Task not found.", parent=self.root)
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("450x280")
        edit_window.configure(bg="#ffffff")
        edit_window.resizable(False, False)
        edit_window.transient(self.root)
        edit_window.grab_set()

        edit_frame = ttk.Frame(edit_window, padding="20")
        edit_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(edit_frame, text="Description:").grid(row=0, column=0, padx=5, pady=(5, 10), sticky="w")
        edit_desc_entry = ttk.Entry(edit_frame, font=("Segoe UI", 10), width=40)
        edit_desc_entry.grid(row=0, column=1, padx=5, pady=(5, 10), ipady=3)
        edit_desc_entry.insert(0, task_to_edit['description'])
        edit_desc_entry.configure(foreground="#333333")

        ttk.Label(edit_frame, text="Priority:").grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")
        edit_priority_var = tk.StringVar(value=task_to_edit.get('priority', 'Medium'))
        edit_priority_cb = ttk.Combobox(edit_frame, textvariable=edit_priority_var,
                                        values=["High", "Medium", "Low"], state="readonly",
                                        width=15, font=("Segoe UI", 10))
        edit_priority_cb.grid(row=1, column=1, padx=5, pady=(5, 10), sticky="w")

        ttk.Label(edit_frame, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=(5, 10), sticky="w")
        edit_due_date_entry = ttk.Entry(edit_frame, font=("Segoe UI", 10), width=18)
        edit_due_date_entry.grid(row=2, column=1, padx=5, pady=(5, 10), sticky="w", ipady=3)
        current_due = task_to_edit.get('due_date')
        edit_due_date_entry.insert(0, current_due if current_due else "Optional")
        edit_due_date_entry.configure(foreground="#aaaaaa" if not current_due else "#333333")
        edit_due_date_entry.bind("<FocusIn>", lambda e: self.clear_placeholder_date(e, "Optional"))
        edit_due_date_entry.bind("<FocusOut>", lambda e: self.add_placeholder_date(e, "Optional"))

        def save_edits_action():
            new_desc = edit_desc_entry.get().strip()
            new_prio = edit_priority_var.get()
            new_due_str = edit_due_date_entry.get().strip()

            if not new_desc:
                messagebox.showwarning("Input Error", "Description cannot be empty.", parent=edit_window)
                return

            valid_new_due = None
            if new_due_str and new_due_str != "Optional":
                try:
                    datetime.strptime(new_due_str, "%Y-%m-%d")
                    valid_new_due = new_due_str
                except ValueError:
                    messagebox.showwarning("Input Error", "Invalid due date format.", parent=edit_window)
                    return
            elif new_due_str == "Optional":
                valid_new_due = None

            task_to_edit.update({
                'description': new_desc,
                'priority': new_prio,
                'due_date': valid_new_due
            })

            self.refresh_task_list()
            self.save_tasks()
            self.status_var.set(f"Task ID {task_id} updated.")
            edit_window.destroy()

        btn_frame = ttk.Frame(edit_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="💾 Save Changes", command=save_edits_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

    def delete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select task(s) to delete.", parent=self.root)
            return

        confirm_msg = (f"Are you sure you want to delete {len(selected)} task(s)?"
                       if len(selected) > 1 else
                       "Are you sure you want to delete the selected task?")

        if messagebox.askyesno("Confirm Delete", confirm_msg, parent=self.root):
            ids_del = {int(iid) for iid in selected if iid.isdigit()}
            self.tasks = [t for t in self.tasks if t.get('id') not in ids_del]
            self.refresh_task_list()
            self.save_tasks()
            self.status_var.set(f"{len(ids_del)} task(s) deleted.")

    def save_tasks(self):
        try:
            with open("todolist_data.json", "w") as f:
                json.dump(self.tasks, f, indent=4)
        except IOError:
            messagebox.showerror("Save Error", "Could not save tasks.", parent=self.root)

    def load_tasks(self):
        try:
            with open("todolist_data.json", "r") as f:
                data = json.load(f)

            self.tasks = []
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    continue

                task_id = item.get('id')
                task_id = int(task_id) if isinstance(task_id, (int, str)) and str(task_id).isdigit() else i + 1

                self.tasks.append({
                    'id': task_id,
                    'description': item.get('description', 'N/A'),
                    'priority': item.get('priority', 'Medium'),
                    'due_date': item.get('due_date'),
                    'status': item.get('status', 'Pending'),
                    'added_date': item.get('added_date', datetime.now().strftime("%Y-%m-%d %H:%M"))
                })
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading tasks: {e}", parent=self.root)
            self.tasks = []

    def on_closing(self):
        self.save_tasks()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernTodoList(root)
    root.mainloop()