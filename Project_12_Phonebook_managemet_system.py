import tkinter as tk
from tkinter import messagebox, ttk
import json
import os


class PhonebookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phonebook Management System")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f8ff")  # Light blue background

        # Load contacts from file
        self.phonebook = self.load_contacts()

        # Create main menu
        self.create_main_menu()

    def load_contacts(self):
        """Load contacts from JSON file if it exists"""
        if os.path.exists("phonebook.json"):
            with open("phonebook.json", "r") as file:
                return json.load(file)
        return {}

    def save_contacts(self):
        """Save contacts to JSON file"""
        with open("phonebook.json", "w") as file:
            json.dump(self.phonebook, file)

    def clear_screen(self):
        """Clear all widgets from the screen"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        """Create the main menu screen"""
        self.clear_screen()

        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f8ff", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Title
        title = tk.Label(
            main_frame,
            text="PHONEBOOK MANAGEMENT SYSTEM",
            font=("Arial", 16, "bold"),
            bg="#4682b4",  # Steel blue
            fg="white",
            padx=10,
            pady=10
        )
        title.pack(fill=tk.X, pady=(0, 20))

        # Menu buttons
        buttons = [
            ("Add Contact", self.add_contact_screen),
            ("View Contacts", self.view_contacts_screen),
            ("Search Contact", self.search_contact_screen),
            ("Delete Contact", self.delete_contact_screen),
            ("Exit", self.exit_app)
        ]

        for text, command in buttons:
            btn = tk.Button(
                main_frame,
                text=text,
                command=command,
                width=20,
                height=2,
                bg="#5f9ea0",  # Cadet blue
                fg="white",
                font=("Arial", 10),
                relief=tk.RAISED,
                bd=2
            )
            btn.pack(pady=5)

    def add_contact_screen(self):
        """Screen for adding new contacts"""
        self.clear_screen()

        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f8ff", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Title
        title = tk.Label(
            main_frame,
            text="Add New Contact",
            font=("Arial", 14, "bold"),
            bg="#4682b4",
            fg="white",
            padx=10,
            pady=10
        )
        title.pack(fill=tk.X, pady=(0, 20))

        # Form frame
        form_frame = tk.Frame(main_frame, bg="#f0f8ff")
        form_frame.pack(pady=10)

        # Form fields
        fields = ["Name:", "Phone:", "Email:", "Address:"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(
                form_frame,
                text=field,
                bg="#f0f8ff",
                font=("Arial", 10)
            ).grid(row=i, column=0, padx=5, pady=5, sticky="e")

            entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field[:-1].lower()] = entry

        # Button frame
        button_frame = tk.Frame(main_frame, bg="#f0f8ff")
        button_frame.pack(pady=20)

        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save Contact",
            command=self.save_contact,
            width=15,
            bg="#2e8b57",  # Sea green
            fg="white",
            font=("Arial", 10)
        )
        save_btn.grid(row=0, column=0, padx=10)

        # Back button
        back_btn = tk.Button(
            button_frame,
            text="Back to Menu",
            command=self.create_main_menu,
            width=15,
            bg="#cd5c5c",  # Indian red
            fg="white",
            font=("Arial", 10)
        )
        back_btn.grid(row=0, column=1, padx=10)

    def save_contact(self):
        """Save the new contact to phonebook"""
        contact = {}
        for field, entry in self.entries.items():
            value = entry.get().strip()
            if not value and field == "name":
                messagebox.showerror("Error", "Name is required!")
                return
            contact[field] = value

        name = contact["name"]
        self.phonebook[name] = contact
        self.save_contacts()

        messagebox.showinfo("Success", f"Contact for {name} saved successfully!")
        self.create_main_menu()

    def view_contacts_screen(self):
        """Screen to view all contacts"""
        self.clear_screen()

        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f8ff", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Title
        title = tk.Label(
            main_frame,
            text="All Contacts",
            font=("Arial", 14, "bold"),
            bg="#4682b4",
            fg="white",
            padx=10,
            pady=10
        )
        title.pack(fill=tk.X, pady=(0, 20))

        if not self.phonebook:
            tk.Label(
                main_frame,
                text="No contacts found.",
                bg="#f0f8ff",
                font=("Arial", 12)
            ).pack(pady=50)
        else:
            # Treeview to display contacts
            tree_frame = tk.Frame(main_frame, bg="#f0f8ff")
            tree_frame.pack(fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(tree_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            tree = ttk.Treeview(
                tree_frame,
                columns=("Name", "Phone", "Email"),
                show="headings",
                yscrollcommand=scrollbar.set
            )

            # Configure columns
            tree.heading("Name", text="Name")
            tree.heading("Phone", text="Phone")
            tree.heading("Email", text="Email")

            tree.column("Name", width=150)
            tree.column("Phone", width=120)
            tree.column("Email", width=180)

            # Add contacts
            for name, details in self.phonebook.items():
                tree.insert("", tk.END, values=(
                    name,
                    details.get("phone", ""),
                    details.get("email", "")
                ))

            tree.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=tree.yview)

        # Back button
        back_btn = tk.Button(
            main_frame,
            text="Back to Menu",
            command=self.create_main_menu,
            width=15,
            bg="#cd5c5c",
            fg="white",
            font=("Arial", 10)
        )
        back_btn.pack(pady=20)

    def search_contact_screen(self):
        """Screen to search for contacts"""
        self.clear_screen()

        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f8ff", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Title
        title = tk.Label(
            main_frame,
            text="Search Contact",
            font=("Arial", 14, "bold"),
            bg="#4682b4",
            fg="white",
            padx=10,
            pady=10
        )
        title.pack(fill=tk.X, pady=(0, 20))

        # Search frame
        search_frame = tk.Frame(main_frame, bg="#f0f8ff")
        search_frame.pack(pady=20)

        tk.Label(
            search_frame,
            text="Enter Name:",
            bg="#f0f8ff",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(search_frame, width=30, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Search button
        search_btn = tk.Button(
            search_frame,
            text="Search",
            command=self.search_contact,
            width=10,
            bg="#5f9ea0",
            fg="white",
            font=("Arial", 10)
        )
        search_btn.pack(side=tk.LEFT, padx=5)

        # Result frame
        self.result_frame = tk.Frame(main_frame, bg="#f0f8ff")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Back button
        back_btn = tk.Button(
            main_frame,
            text="Back to Menu",
            command=self.create_main_menu,
            width=15,
            bg="#cd5c5c",
            fg="white",
            font=("Arial", 10)
        )
        back_btn.pack(pady=20)

    def search_contact(self):
        """Search for a contact by name"""
        name = self.search_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Please enter a name to search!")
            return

        # Clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Search for contact
        found = False
        for contact_name, details in self.phonebook.items():
            if name.lower() in contact_name.lower():
                found = True
                # Display contact details
                details_frame = tk.Frame(
                    self.result_frame,
                    bg="#e6e6fa",  # Lavender
                    padx=10,
                    pady=10,
                    relief=tk.GROOVE,
                    bd=2
                )
                details_frame.pack(fill=tk.X, pady=5, padx=20)

                tk.Label(
                    details_frame,
                    text=f"Name: {contact_name}",
                    font=("Arial", 10, "bold"),
                    bg="#e6e6fa"
                ).pack(anchor="w")

                for field, value in details.items():
                    if field != "name":
                        tk.Label(
                            details_frame,
                            text=f"{field.title()}: {value}",
                            bg="#e6e6fa",
                            font=("Arial", 10)
                        ).pack(anchor="w")

        if not found:
            tk.Label(
                self.result_frame,
                text="No matching contacts found.",
                bg="#f0f8ff",
                font=("Arial", 12)
            ).pack(pady=20)

    def delete_contact_screen(self):
        """Screen to delete contacts"""
        self.clear_screen()

        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f8ff", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Title
        title = tk.Label(
            main_frame,
            text="Delete Contact",
            font=("Arial", 14, "bold"),
            bg="#4682b4",
            fg="white",
            padx=10,
            pady=10
        )
        title.pack(fill=tk.X, pady=(0, 20))

        # Delete frame
        delete_frame = tk.Frame(main_frame, bg="#f0f8ff")
        delete_frame.pack(pady=20)

        tk.Label(
            delete_frame,
            text="Enter Name:",
            bg="#f0f8ff",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.delete_entry = tk.Entry(delete_frame, width=30, font=("Arial", 10))
        self.delete_entry.pack(side=tk.LEFT, padx=5)

        # Delete button
        delete_btn = tk.Button(
            delete_frame,
            text="Delete",
            command=self.delete_contact,
            width=10,
            bg="#cd5c5c",
            fg="white",
            font=("Arial", 10)
        )
        delete_btn.pack(side=tk.LEFT, padx=5)

        # Result label
        self.delete_result = tk.Label(
            main_frame,
            text="",
            bg="#f0f8ff",
            font=("Arial", 10)
        )
        self.delete_result.pack(pady=10)

        # Back button
        back_btn = tk.Button(
            main_frame,
            text="Back to Menu",
            command=self.create_main_menu,
            width=15,
            bg="#cd5c5c",
            fg="white",
            font=("Arial", 10)
        )
        back_btn.pack(pady=20)

    def delete_contact(self):
        """Delete a contact from phonebook"""
        name = self.delete_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Please enter a name to delete!")
            return

        if name in self.phonebook:
            if messagebox.askyesno("Confirm", f"Delete contact for {name}?"):
                del self.phonebook[name]
                self.save_contacts()
                self.delete_result.config(
                    text=f"Contact for {name} deleted successfully!",
                    fg="green"
                )
        else:
            self.delete_result.config(
                text="Contact not found.",
                fg="red"
            )

    def exit_app(self):
        """Exit the application"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PhonebookApp(root)
    root.mainloop()
