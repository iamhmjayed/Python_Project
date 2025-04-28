from PyPDF2 import PdfMerger
from tkinter import *
from tkinter import filedialog, messagebox
import os

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger Tool")
        self.root.geometry("500x300")
        
        # Variables to store file paths
        self.file1_path = StringVar()
        self.file2_path = StringVar()
        self.output_name = StringVar(value="merged.pdf")
        
        # Create GUI elements
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        Label(self.root, text="PDF Merger", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame for file selection
        frame = Frame(self.root)
        frame.pack(pady=10)
        
        # File 1 selection
        Label(frame, text="First PDF:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        Entry(frame, textvariable=self.file1_path, width=30).grid(row=0, column=1, padx=5)
        Button(frame, text="Browse", command=lambda: self.browse_file(1)).grid(row=0, column=2, padx=5)
        
        # File 2 selection
        Label(frame, text="Second PDF:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        Entry(frame, textvariable=self.file2_path, width=30).grid(row=1, column=1, padx=5)
        Button(frame, text="Browse", command=lambda: self.browse_file(2)).grid(row=1, column=2, padx=5)
        
        # Output file name
        Label(frame, text="Output File:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        Entry(frame, textvariable=self.output_name, width=30).grid(row=2, column=1, padx=5)
        
        # Merge button
        Button(self.root, text="Merge PDFs", command=self.merge_pdfs, 
              bg="#4CAF50", fg="white", font=("Arial", 12), padx=20, pady=5).pack(pady=20)
    
    def browse_file(self, file_num):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            if file_num == 1:
                self.file1_path.set(file_path)
            else:
                self.file2_path.set(file_path)
    
    def merge_pdfs(self):
        file1 = self.file1_path.get()
        file2 = self.file2_path.get()
        output = self.output_name.get()
        
        if not file1 or not file2:
            messagebox.showerror("Error", "Please select both PDF files!")
            return
        
        if not output:
            messagebox.showerror("Error", "Please specify an output file name!")
            return
        
        if not output.endswith('.pdf'):
            output += '.pdf'
        
        try:
            merger = PdfMerger()
            
            for pdf in [file1, file2]:
                if not os.path.exists(pdf):
                    messagebox.showerror("Error", f"File not found: {pdf}")
                    return
                merger.append(pdf)
            
            merger.write(output)
            merger.close()
            
            messagebox.showinfo("Success", f"PDFs merged successfully!\nSaved as: {output}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")

# Create and run the application
root = Tk()
app = PDFMergerApp(root)
root.mainloop()
