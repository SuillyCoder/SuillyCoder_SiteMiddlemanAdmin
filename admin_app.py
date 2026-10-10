import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import os
from typing import Dict, List, Optional
from supabase import create_client, Client
import base64


class SupabaseManager:
    """Manages Supabase connection and data operations."""

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client: Optional[Client] = None
        self.connect()

    def connect(self):
        """Establish connection to Supabase."""
        try:
            self.client = create_client(self.url, self.key)
            return True
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            return False

    def insert_project(self, project_data: Dict) -> bool:
        """Insert a project into Supabase."""
        try:
            response = self.client.table('projects').insert(project_data).execute()
            return True
        except Exception as e:
            print(f"Error inserting project: {e}")
            return False

    def insert_certification(self, cert_data: Dict) -> bool:
        """Insert a certification into Supabase."""
        try:
            response = self.client.table('certifications').insert(cert_data).execute()
            return True
        except Exception as e:
            print(f"Error inserting certification: {e}")
            return False

    def insert_skill(self, skill_data: Dict) -> bool:
        """Insert a skill into Supabase."""
        try:
            response = self.client.table('skills').insert(skill_data).execute()
            return True
        except Exception as e:
            print(f"Error inserting skill: {e}")
            return False

    def verify_data_retention(self, table: str) -> bool:
        """Check if data still exists in the specified table."""
        try:
            response = self.client.table(table).select('*').execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error verifying data retention: {e}")
            return False


class ProjectForm:
    """Form for adding/editing projects."""

    def __init__(self, parent, supabase_manager: SupabaseManager):
        self.parent = parent
        self.supabase_manager = supabase_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Add Project")
        self.window.geometry("600x700")
        self.image_path = None
        self.create_widgets()

    def create_widgets(self):
        """Create form widgets."""
        # Category
        tk.Label(self.window, text="Category:").pack(pady=5)
        self.category_var = tk.StringVar(value="fullstack")
        category_frame = tk.Frame(self.window)
        category_frame.pack(pady=5)
        tk.Radiobutton(category_frame, text="FullStack", variable=self.category_var, value="fullstack").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(category_frame, text="DS/AI/ML", variable=self.category_var, value="ds-ai-ml").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(category_frame, text="Hardware/CV", variable=self.category_var, value="hardware-cv").pack(side=tk.LEFT, padx=5)

        # Name
        tk.Label(self.window, text="Project Name:").pack(pady=5)
        self.name_entry = tk.Entry(self.window, width=50)
        self.name_entry.pack(pady=5)

        # Repo Link
        tk.Label(self.window, text="Repository Link:").pack(pady=5)
        self.repo_entry = tk.Entry(self.window, width=50)
        self.repo_entry.pack(pady=5)

        # Description
        tk.Label(self.window, text="Description:").pack(pady=5)
        self.desc_text = tk.Text(self.window, width=50, height=5)
        self.desc_text.pack(pady=5)

        # Tags
        tk.Label(self.window, text="Tags (comma-separated):").pack(pady=5)
        self.tags_entry = tk.Entry(self.window, width=50)
        self.tags_entry.pack(pady=5)

        # Image
        tk.Label(self.window, text="Project Image:").pack(pady=5)
        self.image_label = tk.Label(self.window, text="No image selected", bg="lightgray", width=40, height=10)
        self.image_label.pack(pady=5)
        tk.Button(self.window, text="Select Image", command=self.select_image).pack(pady=5)

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Submit", command=self.submit, bg="green", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=10)

    def select_image(self):
        """Open file dialog to select image."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.webp")]
        )
        if file_path:
            self.image_path = file_path
            self.image_label.config(text=os.path.basename(file_path))

    def submit(self):
        """Submit the project data."""
        name = self.name_entry.get().strip()
        repo = self.repo_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        tags = [tag.strip() for tag in self.tags_entry.get().split(",") if tag.strip()]
        category = self.category_var.get()

        if not name or not repo or not description:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        project_data = {
            "name": name,
            "repo_link": repo,
            "description": description,
            "tags": tags,
            "category": category,
            "image_path": self.image_path or ""
        }

        if self.supabase_manager:
            if self.supabase_manager.insert_project(project_data):
                messagebox.showinfo("Success", "Project added successfully!")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "Failed to add project to database.")
        else:
            # For testing without Supabase
            messagebox.showinfo("Success", "Project data prepared (no database connection).")
            self.window.destroy()


class CertificationForm:
    """Form for adding/editing certifications."""

    def __init__(self, parent, supabase_manager: SupabaseManager):
        self.parent = parent
        self.supabase_manager = supabase_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Add Certification")
        self.window.geometry("500x500")
        self.image_path = None
        self.create_widgets()

    def create_widgets(self):
        """Create form widgets."""
        # Name
        tk.Label(self.window, text="Certification Name:").pack(pady=5)
        self.name_entry = tk.Entry(self.window, width=50)
        self.name_entry.pack(pady=5)

        # Link
        tk.Label(self.window, text="Certificate Link:").pack(pady=5)
        self.link_entry = tk.Entry(self.window, width=50)
        self.link_entry.pack(pady=5)

        # Image
        tk.Label(self.window, text="Certificate Image:").pack(pady=5)
        self.image_label = tk.Label(self.window, text="No image selected", bg="lightgray", width=40, height=10)
        self.image_label.pack(pady=5)
        tk.Button(self.window, text="Select Image", command=self.select_image).pack(pady=5)

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Submit", command=self.submit, bg="green", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=10)

    def select_image(self):
        """Open file dialog to select image."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.webp")]
        )
        if file_path:
            self.image_path = file_path
            self.image_label.config(text=os.path.basename(file_path))

    def submit(self):
        """Submit the certification data."""
        name = self.name_entry.get().strip()
        link = self.link_entry.get().strip()

        if not name or not link:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        cert_data = {
            "name": name,
            "link": link,
            "image_path": self.image_path or ""
        }

        if self.supabase_manager:
            if self.supabase_manager.insert_certification(cert_data):
                messagebox.showinfo("Success", "Certification added successfully!")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "Failed to add certification to database.")
        else:
            messagebox.showinfo("Success", "Certification data prepared (no database connection).")
            self.window.destroy()


class SkillForm:
    """Form for adding/editing skills."""

    def __init__(self, parent, supabase_manager: SupabaseManager):
        self.parent = parent
        self.supabase_manager = supabase_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Add Skill")
        self.window.geometry("500x400")
        self.icon_path = None
        self.create_widgets()

    def create_widgets(self):
        """Create form widgets."""
        # Name
        tk.Label(self.window, text="Skill Name:").pack(pady=5)
        self.name_entry = tk.Entry(self.window, width=50)
        self.name_entry.pack(pady=5)

        # Category
        tk.Label(self.window, text="Category:").pack(pady=5)
        self.category_entry = tk.Entry(self.window, width=50)
        self.category_entry.pack(pady=5)

        # Icon (optional)
        tk.Label(self.window, text="Icon (optional):").pack(pady=5)
        self.icon_label = tk.Label(self.window, text="No icon selected", bg="lightgray", width=40, height=5)
        self.icon_label.pack(pady=5)
        tk.Button(self.window, text="Select Icon", command=self.select_icon).pack(pady=5)

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Submit", command=self.submit, bg="green", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=10)

    def select_icon(self):
        """Open file dialog to select icon."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.svg *.ico")]
        )
        if file_path:
            self.icon_path = file_path
            self.icon_label.config(text=os.path.basename(file_path))

    def submit(self):
        """Submit the skill data."""
        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip()

        if not name or not category:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        skill_data = {
            "name": name,
            "category": category,
            "icon_path": self.icon_path or ""
        }

        if self.supabase_manager:
            if self.supabase_manager.insert_skill(skill_data):
                messagebox.showinfo("Success", "Skill added successfully!")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "Failed to add skill to database.")
        else:
            messagebox.showinfo("Success", "Skill data prepared (no database connection).")
            self.window.destroy()


class AdminApp:
    """Main admin application."""

    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Admin - Middleman Application")
        self.root.geometry("800x600")

        # Supabase configuration
        self.supabase_url = ""
        self.supabase_key = ""
        self.supabase_manager = None

        self.create_widgets()

    def create_widgets(self):
        """Create main application widgets."""
        # Header
        header_frame = tk.Frame(self.root, bg="darkblue", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="Portfolio Admin - Middleman Application",
            font=("Arial", 20, "bold"),
            bg="darkblue",
            fg="white"
        ).pack(expand=True)

        # Main content
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Navigation buttons
        nav_frame = tk.Frame(main_frame)
        nav_frame.pack(pady=20)

        tk.Button(
            nav_frame,
            text="Add Project",
            font=("Arial", 14),
            width=20,
            height=2,
            command=self.open_project_form
        ).pack(pady=10)

        tk.Button(
            nav_frame,
            text="Add Certification",
            font=("Arial", 14),
            width=20,
            height=2,
            command=self.open_certification_form
        ).pack(pady=10)

        tk.Button(
            nav_frame,
            text="Add Skill",
            font=("Arial", 14),
            width=20,
            height=2,
            command=self.open_skill_form
        ).pack(pady=10)

        # Supabase configuration section
        config_frame = tk.LabelFrame(main_frame, text="Supabase Configuration", padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=20)

        tk.Label(config_frame, text="Supabase URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = tk.Entry(config_frame, width=50, show="*")
        self.url_entry.grid(row=0, column=1, pady=5)

        tk.Label(config_frame, text="Supabase Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.key_entry = tk.Entry(config_frame, width=50, show="*")
        self.key_entry.grid(row=1, column=1, pady=5)

        tk.Button(config_frame, text="Connect", command=self.connect_supabase).grid(row=2, column=1, pady=10)

        # Data verification section
        verify_frame = tk.LabelFrame(main_frame, text="Data Verification", padx=10, pady=10)
        verify_frame.pack(fill=tk.X, pady=20)

        tk.Button(
            verify_frame,
            text="Verify Projects Data",
            command=lambda: self.verify_data("projects")
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            verify_frame,
            text="Verify Certifications Data",
            command=lambda: self.verify_data("certifications")
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            verify_frame,
            text="Verify Skills Data",
            command=lambda: self.verify_data("skills")
        ).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready - No database connection",
            bg="lightgray",
            relief=tk.SUNKEN
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def connect_supabase(self):
        """Connect to Supabase with provided credentials."""
        url = self.url_entry.get().strip()
        key = self.key_entry.get().strip()

        if not url or not key:
            messagebox.showerror("Error", "Please provide both URL and Key.")
            return

        self.supabase_manager = SupabaseManager(url, key)
        if self.supabase_manager.client:
            self.status_label.config(text="Connected to Supabase")
            messagebox.showinfo("Success", "Successfully connected to Supabase!")
        else:
            self.status_label.config(text="Failed to connect to Supabase")
            messagebox.showerror("Error", "Failed to connect to Supabase.")

    def open_project_form(self):
        """Open the project form."""
        ProjectForm(self.root, self.supabase_manager)

    def open_certification_form(self):
        """Open the certification form."""
        CertificationForm(self.root, self.supabase_manager)

    def open_skill_form(self):
        """Open the skill form."""
        SkillForm(self.root, self.supabase_manager)

    def verify_data(self, table: str):
        """Verify data retention in the specified table."""
        if not self.supabase_manager or not self.supabase_manager.client:
            messagebox.showerror("Error", "Please connect to Supabase first.")
            return

        if self.supabase_manager.verify_data_retention(table):
            messagebox.showinfo("Verification", f"Data exists in {table} table.")
        else:
            messagebox.showwarning("Verification", f"No data found in {table} table.")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
