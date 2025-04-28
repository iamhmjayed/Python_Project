import tkinter as tk
from tkinter import messagebox, ttk


class PhonebookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phonebook Management System")
        self.root.geometry("600x500")

        self.phonebook = {}

        # Create main frame
        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # Title label
        self.title_label = tk.Label(
            self.main_frame,
            text="PHONEBOOK MANAGEMENT SYSTEM",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(pady=10)

        # Create buttons for menu options
        button_options = [
            ("Add Contact", self.add_contact),
            ("View Phonebook", self.view_phonebook),
            ("Search Contact", self.search_contact),
            ("Delete Contact", self.delete_contact),
            ("About Developer", self.about_developer),
            ("Exit", self.exit_app)
        ]

        for text, command in button_options:
            btn = tk.Button(
                self.main_frame,
                text=text,
                command=command,
                width=20,
                height=2,
                bg="#4CAF50",
                fg="white",
                font=("Arial", 10)
            )
            btn.pack(pady=5)

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def back_to_main(self):
        self.clear_frame(self.main_frame)
        self.__init__(self.root)

    def add_contact(self):
        self.clear_frame(self.main_frame)

        # Title
        tk.Label(self.main_frame, text="Add New Contact", font=("Arial", 14)).pack(pady=10)

        # Create form frame
        form_frame = tk.Frame(self.main_frame)
        form_frame.pack(pady=10)

        # Name
        tk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = tk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Age
        tk.Label(form_frame, text="Age:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        age_entry = tk.Entry(form_frame, width=30)
        age_entry.grid(row=1, column=1, padx=5, pady=5)

        # Phone
        tk.Label(form_frame, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        phone_entry = tk.Entry(form_frame, width=30)
        phone_entry.grid(row=2, column=1, padx=5, pady=5)

        # Submit button
        submit_btn = tk.Button(
            self.main_frame,
            text="Add Contact",
            command=lambda: self.save_contact(
                name_entry.get(),
                age_entry.get(),
                phone_entry.get()
            ),
            width=15,
            bg="#2196F3",
            fg="white"
        )
        submit_btn.pack(pady=10)

        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="Back to Menu",
            command=self.back_to_main,
            width=15,
            bg="#f44336",
            fg="white"
        )
        back_btn.pack(pady=5)

    def save_contact(self, name, age, phone):
        if not name or not age or not phone:
            messagebox.showerror("Error", "All fields are required!")
            return

        self.phonebook[name] = {'age': age, 'phone': phone}
        messagebox.showinfo("Success", f"Contact for {name} added successfully!")

    def view_phonebook(self):
        self.clear_frame(self.main_frame)

        # Title
        tk.Label(self.main_frame, text="Phonebook Contacts", font=("Arial", 14)).pack(pady=10)

        if not self.phonebook:
            tk.Label(self.main_frame, text="Phonebook is empty.").pack(pady=10)
        else:
            # Create treeview to display contacts
            tree = ttk.Treeview(self.main_frame, columns=("Name", "Age", "Phone"), show="headings")
            tree.heading("Name", text="Name")
            tree.heading("Age", text="Age")
            tree.heading("Phone", text="Phone")

            # Add contacts to treeview
            for name, details in self.phonebook.items():
                tree.insert("", tk.END, values=(name, details['age'], details['phone']))

            tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="Back to Menu",
            command=self.back_to_main,
            width=15,
            bg="#f44336",
            fg="white"
        )
        back_btn.pack(pady=10)

    def search_contact(self):
        self.clear_frame(self.main_frame)

        # Title
        tk.Label(self.main_frame, text="Search Contact", font=("Arial", 14)).pack(pady=10)

        # Search frame
        search_frame = tk.Frame(self.main_frame)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Enter Name:").pack(side=tk.LEFT, padx=5)
        search_entry = tk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)

        # Result label
        result_label = tk.Label(self.main_frame, text="", wraplength=400)
        result_label.pack(pady=10)

        # Search button
        search_btn = tk.Button(
            self.main_frame,
            text="Search",
            command=lambda: self.perform_search(search_entry.get(), result_label),
            width=15,
            bg="#2196F3",
            fg="white"
        )
        search_btn.pack(pady=5)

        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="Back to Menu",
            command=self.back_to_main,
            width=15,
            bg="#f44336",
            fg="white"
        )
        back_btn.pack(pady=5)

    def perform_search(self, name, result_label):
        if not name:
            messagebox.showerror("Error", "Please enter a name to search!")
            return

        if name in self.phonebook:
            details = self.phonebook[name]
            result_label.config(
                text=f"Name: {name}\nAge: {details['age']}\nPhone: {details['phone']}",
                fg="green"
            )
        else:
            result_label.config(text="Contact not found.", fg="red")

    def delete_contact(self):
        self.clear_frame(self.main_frame)

        # Title
        tk.Label(self.main_frame, text="Delete Contact", font=("Arial", 14)).pack(pady=10)

        # Delete frame
        delete_frame = tk.Frame(self.main_frame)
        delete_frame.pack(pady=10)

        tk.Label(delete_frame, text="Enter Name:").pack(side=tk.LEFT, padx=5)
        delete_entry = tk.Entry(delete_frame, width=30)
        delete_entry.pack(side=tk.LEFT, padx=5)

        # Result label
        result_label = tk.Label(self.main_frame, text="", wraplength=400)
        result_label.pack(pady=10)

        # Delete button
        delete_btn = tk.Button(
            self.main_frame,
            text="Delete",
            command=lambda: self.perform_delete(delete_entry.get(), result_label),
            width=15,
            bg="#2196F3",
            fg="white"
        )
        delete_btn.pack(pady=5)

        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="Back to Menu",
            command=self.back_to_main,
            width=15,
            bg="#f44336",
            fg="white"
        )
        back_btn.pack(pady=5)

    def perform_delete(self, name, result_label):
        if not name:
            messagebox.showerror("Error", "Please enter a name to delete!")
            return

        if name in self.phonebook:
            del self.phonebook[name]
            result_label.config(text=f"Contact for {name} deleted successfully!", fg="green")
        else:
            result_label.config(text="Contact not found.", fg="red")

    def about_developer(self):
        self.clear_frame(self.main_frame)

        # Title
        tk.Label(self.main_frame, text="About Developer", font=("Arial", 14)).pack(pady=10)

        # Developer info
        info = "This Phonebook Management System is developed by Hossain Mohammad Jayed."
        tk.Label(self.main_frame, text=info, wraplength=400).pack(pady=20)

        # Back button
        back_btn = tk.Button(
            self.main_frame,
            text="Back to Menu",
            command=self.back_to_main,
            width=15,
            bg="#f44336",
            fg="white"
        )
        back_btn.pack(pady=10)

    def exit_app(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PhonebookApp(root)
    root.mainloop()
