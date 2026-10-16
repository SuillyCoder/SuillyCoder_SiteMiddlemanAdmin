import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import os
from typing import Dict, List, Optional
from supabase import create_client, Client
import base64
from pathlib import Path
from dotenv import load_dotenv


class SupabaseManager:
    """Manages Supabase connection and data operations."""

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client: Optional[Client] = None
        self.last_error = ""
        self._initialize_connection()

    def _initialize_connection(self):
        """Initialize the connection without returning a tuple."""
        try:
            self.client = create_client(self.url, self.key)
        except Exception as e:
            self.last_error = str(e)

    def connect(self) -> tuple[bool, str]:
        """Establish connection to Supabase."""
        try:
            self.client = create_client(self.url, self.key)
            return True, "Connected successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            if "Invalid URL" in error_msg or "invalid" in error_msg.lower():
                return False, "Invalid Supabase URL provided"
            elif "API key" in error_msg.lower() or "key" in error_msg.lower():
                return False, "Invalid Supabase API key provided"
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                return False, "Network error: Could not connect to Supabase"
            else:
                return False, f"Connection error: {error_msg}"

    def insert_project(self, project_data: Dict) -> tuple[bool, str]:
        """Insert a project into Supabase."""
        try:
            response = self.client.table('projects').insert(project_data).execute()
            return True, "Project added successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
                return False, "Table 'projects' does not exist in Supabase. Please create it first."
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                return False, "Permission denied: Check Row Level Security (RLS) policies for 'projects' table"
            elif "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                return False, "Duplicate entry: A project with this name may already exist"
            elif "column" in error_msg.lower():
                return False, f"Column error: {error_msg}. Check if table schema matches data structure."
            else:
                return False, f"Failed to add project: {error_msg}"

    def insert_certification(self, cert_data: Dict) -> tuple[bool, str]:
        """Insert a certification into Supabase."""
        try:
            response = self.client.table('certifications').insert(cert_data).execute()
            return True, "Certification added successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
                return False, "Table 'certifications' does not exist in Supabase. Please create it first."
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                return False, "Permission denied: Check Row Level Security (RLS) policies for 'certifications' table"
            elif "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                return False, "Duplicate entry: A certification with this name may already exist"
            elif "column" in error_msg.lower():
                return False, f"Column error: {error_msg}. Check if table schema matches data structure."
            else:
                return False, f"Failed to add certification: {error_msg}"

    def insert_skill(self, skill_data: Dict) -> tuple[bool, str]:
        """Insert a skill into Supabase."""
        try:
            response = self.client.table('skills').insert(skill_data).execute()
            return True, "Skill added successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
                return False, "Table 'skills' does not exist in Supabase. Please create it first."
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                return False, "Permission denied: Check Row Level Security (RLS) policies for 'skills' table"
            elif "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                return False, "Duplicate entry: A skill with this name may already exist"
            elif "column" in error_msg.lower():
                return False, f"Column error: {error_msg}. Check if table schema matches data structure."
            else:
                return False, f"Failed to add skill: {error_msg}"

    def verify_data_retention(self, table: str) -> tuple[bool, str]:
        """Check if data still exists in the specified table."""
        try:
            response = self.client.table(table).select('*').execute()
            if len(response.data) > 0:
                return True, f"Found {len(response.data)} records in {table} table"
            else:
                return False, f"No data found in {table} table"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
                return False, f"Table '{table}' does not exist in Supabase"
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                return False, f"Permission denied: Cannot access '{table}' table"
            else:
                return False, f"Failed to verify data: {error_msg}"

    def upload_image(self, file_path: str, bucket_name: str = "Site_Images") -> tuple[bool, str, Optional[str]]:
        """
        Upload an image to Supabase Storage.

        Args:
            file_path: Local path to the image file
            bucket_name: Name of the storage bucket (default: "Site_Images")

        Returns:
            Tuple of (success: bool, message: str, public_url: Optional[str])
        """
        try:
            # Generate a unique filename
            file_extension = Path(file_path).suffix
            import uuid
            unique_filename = f"{uuid.uuid4()}{file_extension}"

            # Read the file
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Upload to Supabase Storage
            self.client.storage.from_(bucket_name).upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": self._get_mime_type(file_extension)}
            )

            # Get the public URL
            public_url = self.client.storage.from_(bucket_name).get_public_url(unique_filename)

            return True, "Image uploaded successfully", public_url

        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            if "bucket" in error_msg.lower() and "not found" in error_msg.lower():
                return False, f"Storage bucket '{bucket_name}' not found. Please create it in Supabase.", None
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                return False, f"Permission denied: Check storage bucket policies for '{bucket_name}'", None
            elif "size" in error_msg.lower():
                return False, f"File size error: {error_msg}", None
            else:
                return False, f"Failed to upload image: {error_msg}", None

    def _get_mime_type(self, file_extension: str) -> str:
        """Get MIME type based on file extension."""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.pdf': 'application/pdf'
        }
        return mime_types.get(file_extension.lower(), 'application/octet-stream')

    def get_all_projects(self) -> tuple[bool, str, List[Dict]]:
        """Get all projects from Supabase."""
        try:
            response = self.client.table('projects').select('*').execute()
            return True, "Projects retrieved successfully", response.data
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            return False, f"Failed to retrieve projects: {error_msg}", []

    def get_all_certifications(self) -> tuple[bool, str, List[Dict]]:
        """Get all certifications from Supabase."""
        try:
            response = self.client.table('certifications').select('*').execute()
            return True, "Certifications retrieved successfully", response.data
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            return False, f"Failed to retrieve certifications: {error_msg}", []

    def get_all_skills(self) -> tuple[bool, str, List[Dict]]:
        """Get all skills from Supabase."""
        try:
            response = self.client.table('skills').select('*').execute()
            return True, "Skills retrieved successfully", response.data
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            return False, f"Failed to retrieve skills: {error_msg}", []

    def update_project(self, project_id: int, project_data: Dict) -> tuple[bool, str]:
        """Update a project in Supabase."""
        try:
            response = self.client.table('projects').update(project_data).eq('id', project_id).execute()
            return True, "Project updated successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            return False, f"Failed to update project: {error_msg}"

    def update_certification(self, cert_id: int, cert_data: Dict) -> tuple[bool, str]:
        """Update a certification in Supabase."""
        try:
            response = self.client.table('certifications').update(cert_data).eq('id', cert_id).execute()
            return True, "Certification updated successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            return False, f"Failed to update certification: {error_msg}"

    def update_skill(self, skill_id: int, skill_data: Dict) -> tuple[bool, str]:
        """Update a skill in Supabase."""
        try:
            response = self.client.table('skills').update(skill_data).eq('id', skill_id).execute()
            return True, "Skill updated successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            return False, f"Failed to update skill: {error_msg}"

    def delete_project(self, project_id: int) -> tuple[bool, str]:
        """Delete a project from Supabase."""
        try:
            response = self.client.table('projects').delete().eq('id', project_id).execute()
            return True, "Project deleted successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            return False, f"Failed to delete project: {error_msg}"

    def delete_certification(self, cert_id: int) -> tuple[bool, str]:
        """Delete a certification from Supabase."""
        try:
            response = self.client.table('certifications').delete().eq('id', cert_id).execute()
            return True, "Certification deleted successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            return False, f"Failed to delete certification: {error_msg}"

    def delete_skill(self, skill_id: int) -> tuple[bool, str]:
        """Delete a skill from Supabase."""
        try:
            response = self.client.table('skills').delete().eq('id', skill_id).execute()
            return True, "Skill deleted successfully"
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            return False, f"Failed to delete skill: {error_msg}"


class ProjectForm:
    """Form for adding/editing projects."""

    def __init__(self, parent, supabase_manager: SupabaseManager, project_data: Optional[Dict] = None):
        self.parent = parent
        self.supabase_manager = supabase_manager
        self.project_data = project_data
        self.edit_mode = project_data is not None
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Project" if self.edit_mode else "Add Project")
        self.window.geometry("600x700")
        self.image_path = None
        self.current_image_url = project_data.get('image_path', '') if self.edit_mode else ''
        self.create_widgets()

        if self.edit_mode:
            self.populate_fields()

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
            # Show image preview
            try:
                image = Image.open(file_path)
                image.thumbnail((300, 200))  # Resize for preview
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo  # Keep reference
            except Exception as e:
                self.image_label.config(text=os.path.basename(file_path))

    def populate_fields(self):
        """Populate form fields with existing project data."""
        if not self.project_data:
            return

        self.name_entry.insert(0, self.project_data.get('name', ''))
        self.repo_entry.insert(0, self.project_data.get('repo_link', ''))
        self.desc_text.insert("1.0", self.project_data.get('description', ''))
        self.tags_entry.insert(0, ', '.join(self.project_data.get('tags', [])))
        self.category_var.set(self.project_data.get('category', 'fullstack'))

        if self.current_image_url:
            try:
                # Try to load and display the current image from URL
                import requests
                from io import BytesIO
                response = requests.get(self.current_image_url)
                image = Image.open(BytesIO(response.content))
                image.thumbnail((300, 200))
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo
            except:
                self.image_label.config(text="Current image loaded")

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

        # Upload image to Supabase Storage if provided
        image_url = self.current_image_url  # Keep existing URL if no new image
        if self.image_path and self.supabase_manager:
            success, message, url = self.supabase_manager.upload_image(self.image_path)
            if success:
                image_url = url
            else:
                messagebox.showerror("Error", f"Failed to upload image: {message}")
                return
        elif self.image_path and not self.supabase_manager:
            # For testing without Supabase - use local path
            image_url = self.image_path

        project_data = {
            "name": name,
            "repo_link": repo,
            "description": description,
            "tags": tags,
            "category": category,
            "image_path": image_url
        }

        if self.supabase_manager:
            if self.edit_mode:
                success, message = self.supabase_manager.update_project(self.project_data['id'], project_data)
            else:
                success, message = self.supabase_manager.insert_project(project_data)

            if success:
                messagebox.showinfo("Success", message)
                self.window.destroy()
            else:
                messagebox.showerror("Error", message)
        else:
            # For testing without Supabase
            messagebox.showinfo("Success", "Project data prepared (no database connection).")
            self.window.destroy()


class CertificationForm:
    """Form for adding/editing certifications."""

    def __init__(self, parent, supabase_manager: SupabaseManager, cert_data: Optional[Dict] = None):
        self.parent = parent
        self.supabase_manager = supabase_manager
        self.cert_data = cert_data
        self.edit_mode = cert_data is not None
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Certification" if self.edit_mode else "Add Certification")
        self.window.geometry("500x500")
        self.image_path = None
        self.current_image_url = cert_data.get('image_path', '') if self.edit_mode else ''
        self.create_widgets()

        if self.edit_mode:
            self.populate_fields()

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
            # Show image preview
            try:
                image = Image.open(file_path)
                image.thumbnail((300, 200))  # Resize for preview
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo  # Keep reference
            except Exception as e:
                self.image_label.config(text=os.path.basename(file_path))

    def populate_fields(self):
        """Populate form fields with existing certification data."""
        if not self.cert_data:
            return

        self.name_entry.insert(0, self.cert_data.get('name', ''))
        self.link_entry.insert(0, self.cert_data.get('link', ''))

        if self.current_image_url:
            try:
                import requests
                from io import BytesIO
                response = requests.get(self.current_image_url)
                image = Image.open(BytesIO(response.content))
                image.thumbnail((300, 200))
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo
            except:
                self.image_label.config(text="Current image loaded")

    def submit(self):
        """Submit the certification data."""
        name = self.name_entry.get().strip()
        link = self.link_entry.get().strip()

        if not name or not link:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        # Upload image to Supabase Storage if provided
        image_url = self.current_image_url  # Keep existing URL if no new image
        if self.image_path and self.supabase_manager:
            success, message, url = self.supabase_manager.upload_image(self.image_path)
            if success:
                image_url = url
            else:
                messagebox.showerror("Error", f"Failed to upload image: {message}")
                return
        elif self.image_path and not self.supabase_manager:
            # For testing without Supabase - use local path
            image_url = self.image_path

        cert_data = {
            "name": name,
            "link": link,
            "image_path": image_url
        }

        if self.supabase_manager:
            if self.edit_mode:
                success, message = self.supabase_manager.update_certification(self.cert_data['id'], cert_data)
            else:
                success, message = self.supabase_manager.insert_certification(cert_data)

            if success:
                messagebox.showinfo("Success", message)
                self.window.destroy()
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Success", "Certification data prepared (no database connection).")
            self.window.destroy()


class SkillForm:
    """Form for adding/editing skills."""

    def __init__(self, parent, supabase_manager: SupabaseManager, skill_data: Optional[Dict] = None):
        self.parent = parent
        self.supabase_manager = supabase_manager
        self.skill_data = skill_data
        self.edit_mode = skill_data is not None
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Skill" if self.edit_mode else "Add Skill")
        self.window.geometry("500x400")
        self.window.resizable(True, True)
        self.icon_path = None
        self.current_icon_url = skill_data.get('icon_path', '') if self.edit_mode else ''
        self.create_widgets()

        if self.edit_mode:
            self.populate_fields()

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

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Submit", command=self.submit, bg="green", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=10)

    def populate_fields(self):
        """Populate form fields with existing skill data."""
        if not self.skill_data:
            return

        self.name_entry.insert(0, self.skill_data.get('name', ''))
        self.category_entry.insert(0, self.skill_data.get('category', ''))


class ProjectListDialog:
    """Dialog to view and manage projects."""

    def __init__(self, parent, supabase_manager: SupabaseManager, projects: List[Dict]):
        self.parent = parent
        self.supabase_manager = supabase_manager
        self.projects = projects
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Projects")
        self.window.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        """Create the list view."""
        # Treeview to display projects
        columns = ('name', 'category', 'repo_link')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings')
        self.tree.heading('name', text='Name')
        self.tree.heading('category', text='Category')
        self.tree.heading('repo_link', text='Repository Link')
        self.tree.column('name', width=200)
        self.tree.column('category', width=100)
        self.tree.column('repo_link', width=300)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Populate the tree
        for project in self.projects:
            self.tree.insert('', tk.END, values=(
                project.get('name', ''),
                project.get('category', ''),
                project.get('repo_link', '')
            ), iid=project['id'])

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Selected", command=self.delete_selected, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def edit_selected(self):
        """Edit the selected project."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a project to edit.")
            return

        project_id = int(selected[0])
        project = next((p for p in self.projects if p['id'] == project_id), None)
        if project:
            self.window.destroy()
            ProjectForm(self.parent, self.supabase_manager, project)

    def delete_selected(self):
        """Delete the selected project."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a project to delete.")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this project?"):
            return

        project_id = int(selected[0])
        success, message = self.supabase_manager.delete_project(project_id)
        if success:
            messagebox.showinfo("Success", message)
            self.window.destroy()
        else:
            messagebox.showerror("Error", message)


class CertificationListDialog:
    """Dialog to view and manage certifications."""

    def __init__(self, parent, supabase_manager: SupabaseManager, certifications: List[Dict]):
        self.parent = parent
        self.supabase_manager = supabase_manager
        self.certifications = certifications
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Certifications")
        self.window.geometry("700x500")
        self.create_widgets()

    def create_widgets(self):
        """Create the list view."""
        columns = ('name', 'link')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings')
        self.tree.heading('name', text='Name')
        self.tree.heading('link', text='Link')
        self.tree.column('name', width=200)
        self.tree.column('link', width=400)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for cert in self.certifications:
            self.tree.insert('', tk.END, values=(
                cert.get('name', ''),
                cert.get('link', '')
            ), iid=cert['id'])

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Selected", command=self.delete_selected, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def edit_selected(self):
        """Edit the selected certification."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a certification to edit.")
            return

        cert_id = int(selected[0])
        cert = next((c for c in self.certifications if c['id'] == cert_id), None)
        if cert:
            self.window.destroy()
            CertificationForm(self.parent, self.supabase_manager, cert)

    def delete_selected(self):
        """Delete the selected certification."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a certification to delete.")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this certification?"):
            return

        cert_id = int(selected[0])
        success, message = self.supabase_manager.delete_certification(cert_id)
        if success:
            messagebox.showinfo("Success", message)
            self.window.destroy()
        else:
            messagebox.showerror("Error", message)


class SkillListDialog:
    """Dialog to view and manage skills."""

    def __init__(self, parent, supabase_manager: SupabaseManager, skills: List[Dict]):
        self.parent = parent
        self.supabase_manager = supabase_manager
        self.skills = skills
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Skills")
        self.window.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        """Create the list view."""
        columns = ('name', 'category')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings')
        self.tree.heading('name', text='Name')
        self.tree.heading('category', text='Category')
        self.tree.column('name', width=200)
        self.tree.column('category', width=300)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for skill in self.skills:
            self.tree.insert('', tk.END, values=(
                skill.get('name', ''),
                skill.get('category', '')
            ), iid=skill['id'])

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Selected", command=self.delete_selected, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def edit_selected(self):
        """Edit the selected skill."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a skill to edit.")
            return

        skill_id = int(selected[0])
        skill = next((s for s in self.skills if s['id'] == skill_id), None)
        if skill:
            self.window.destroy()
            SkillForm(self.parent, self.supabase_manager, skill)

    def delete_selected(self):
        """Delete the selected skill."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a skill to delete.")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this skill?"):
            return

        skill_id = int(selected[0])
        success, message = self.supabase_manager.delete_skill(skill_id)
        if success:
            messagebox.showinfo("Success", message)
            self.window.destroy()
        else:
            messagebox.showerror("Error", message)

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
            "icon_path": ""
        }

        if self.supabase_manager:
            if self.edit_mode:
                success, message = self.supabase_manager.update_skill(self.skill_data['id'], skill_data)
            else:
                success, message = self.supabase_manager.insert_skill(skill_data)

            if success:
                messagebox.showinfo("Success", message)
                self.window.destroy()
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Success", "Skill data prepared (no database connection).")
            self.window.destroy()


class AdminApp:
    """Main admin application."""

    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Admin - Middleman Application")
        self.root.geometry("800x600")

        # Load environment variables
        load_dotenv()

        # Supabase configuration
        self.supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
        self.supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", "")
        self.supabase_manager = None

        # Auto-connect if credentials are available
        if self.supabase_url and self.supabase_key:
            self.auto_connect()

        self.create_widgets()

    def auto_connect(self):
        """Automatically connect to Supabase using environment variables."""
        self.supabase_manager = SupabaseManager(self.supabase_url, self.supabase_key)
        if self.supabase_manager.client:
            print("Auto-connected to Supabase successfully")
        else:
            print(f"Auto-connection failed: {self.supabase_manager.last_error}")

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

        # Projects section
        project_frame = tk.LabelFrame(main_frame, text="Projects", padx=10, pady=10)
        project_frame.pack(fill=tk.X, pady=10)
        project_btn_frame = tk.Frame(project_frame)
        project_btn_frame.pack()
        tk.Button(project_btn_frame, text="Add Project", font=("Arial", 12), width=15, command=self.open_project_form).pack(side=tk.LEFT, padx=5)
        tk.Button(project_btn_frame, text="View/Edit Projects", font=("Arial", 12), width=15, command=self.view_projects).pack(side=tk.LEFT, padx=5)

        # Certifications section
        cert_frame = tk.LabelFrame(main_frame, text="Certifications", padx=10, pady=10)
        cert_frame.pack(fill=tk.X, pady=10)
        cert_btn_frame = tk.Frame(cert_frame)
        cert_btn_frame.pack()
        tk.Button(cert_btn_frame, text="Add Certification", font=("Arial", 12), width=15, command=self.open_certification_form).pack(side=tk.LEFT, padx=5)
        tk.Button(cert_btn_frame, text="View/Edit Certifications", font=("Arial", 12), width=15, command=self.view_certifications).pack(side=tk.LEFT, padx=5)

        # Skills section
        skill_frame = tk.LabelFrame(main_frame, text="Skills", padx=10, pady=10)
        skill_frame.pack(fill=tk.X, pady=10)
        skill_btn_frame = tk.Frame(skill_frame)
        skill_btn_frame.pack()
        tk.Button(skill_btn_frame, text="Add Skill", font=("Arial", 12), width=15, command=self.open_skill_form).pack(side=tk.LEFT, padx=5)
        tk.Button(skill_btn_frame, text="View/Edit Skills", font=("Arial", 12), width=15, command=self.view_skills).pack(side=tk.LEFT, padx=5)

        # Supabase configuration section
        config_frame = tk.LabelFrame(main_frame, text="Supabase Configuration", padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=20)

        tk.Label(config_frame, text="Supabase URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = tk.Entry(config_frame, width=50, show="*")
        self.url_entry.grid(row=0, column=1, pady=5)
        if self.supabase_url:
            self.url_entry.insert(0, self.supabase_url)

        tk.Label(config_frame, text="Supabase Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.key_entry = tk.Entry(config_frame, width=50, show="*")
        self.key_entry.grid(row=1, column=1, pady=5)
        if self.supabase_key:
            self.key_entry.insert(0, self.supabase_key)

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
            text="Connected to Supabase" if self.supabase_manager and self.supabase_manager.client else "Ready - No database connection",
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
            messagebox.showerror("Error", self.supabase_manager.last_error)

    def open_project_form(self):
        """Open the project form."""
        ProjectForm(self.root, self.supabase_manager)

    def open_certification_form(self):
        """Open the certification form."""
        CertificationForm(self.root, self.supabase_manager)

    def open_skill_form(self):
        """Open the skill form."""
        SkillForm(self.root, self.supabase_manager)

    def view_projects(self):
        """View and manage projects."""
        if not self.supabase_manager or not self.supabase_manager.client:
            messagebox.showerror("Error", "Please connect to Supabase first.")
            return

        success, message, projects = self.supabase_manager.get_all_projects()
        if not success:
            messagebox.showerror("Error", message)
            return

        ProjectListDialog(self.root, self.supabase_manager, projects)

    def view_certifications(self):
        """View and manage certifications."""
        if not self.supabase_manager or not self.supabase_manager.client:
            messagebox.showerror("Error", "Please connect to Supabase first.")
            return

        success, message, certs = self.supabase_manager.get_all_certifications()
        if not success:
            messagebox.showerror("Error", message)
            return

        CertificationListDialog(self.root, self.supabase_manager, certs)

    def view_skills(self):
        """View and manage skills."""
        if not self.supabase_manager or not self.supabase_manager.client:
            messagebox.showerror("Error", "Please connect to Supabase first.")
            return

        success, message, skills = self.supabase_manager.get_all_skills()
        if not success:
            messagebox.showerror("Error", message)
            return

        SkillListDialog(self.root, self.supabase_manager, skills)

    def verify_data(self, table: str):
        """Verify data retention in the specified table."""
        if not self.supabase_manager or not self.supabase_manager.client:
            messagebox.showerror("Error", "Please connect to Supabase first.")
            return

        success, message = self.supabase_manager.verify_data_retention(table)
        if success:
            messagebox.showinfo("Verification", message)
        else:
            messagebox.showwarning("Verification", message)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
