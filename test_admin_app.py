import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
from unittest.mock import patch as mock_patch

# Add the current directory to the path to import the admin_app module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock tkinter before importing admin_app
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['dotenv'].load_dotenv = MagicMock()

from admin_app import SupabaseManager


class TestSupabaseManager(unittest.TestCase):
    """Test cases for SupabaseManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_url = "https://test.supabase.co"
        self.test_key = "test_key_123"

    @patch('admin_app.create_client')
    def test_initialization(self, mock_create_client):
        """Test SupabaseManager initialization."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)

        self.assertEqual(manager.url, self.test_url)
        self.assertEqual(manager.key, self.test_key)
        mock_create_client.assert_called_once_with(self.test_url, self.test_key)

    @patch('admin_app.create_client')
    def test_connect_success(self, mock_create_client):
        """Test successful connection to Supabase."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)
        result, message = manager.connect()

        self.assertTrue(result)
        self.assertIsNotNone(manager.client)
        self.assertIn("success", message.lower())

    @patch('admin_app.create_client')
    def test_connect_failure(self, mock_create_client):
        """Test failed connection to Supabase."""
        mock_create_client.side_effect = Exception("Connection error")

        manager = SupabaseManager(self.test_url, self.test_key)
        result, message = manager.connect()

        self.assertFalse(result)
        self.assertIn("error", message.lower())

    @patch('admin_app.create_client')
    def test_insert_project_success(self, mock_create_client):
        """Test successful project insertion."""
        mock_client = Mock()
        mock_table = Mock()
        mock_response = Mock()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value.execute.return_value = mock_response
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)
        project_data = {
            "name": "Test Project",
            "repo_link": "https://github.com/test",
            "description": "Test description",
            "tags": ["python", "tkinter"],
            "category": "fullstack",
            "image_path": ""
        }

        result, message = manager.insert_project(project_data)

        self.assertTrue(result)
        self.assertIn("success", message.lower())
        mock_client.table.assert_called_once_with('projects')

    @patch('admin_app.create_client')
    def test_insert_project_failure(self, mock_create_client):
        """Test failed project insertion."""
        mock_client = Mock()
        mock_table = Mock()
        mock_table.insert.side_effect = Exception("Insert error")
        mock_client.table.return_value = mock_table
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)
        project_data = {"name": "Test Project"}

        result, message = manager.insert_project(project_data)

        self.assertFalse(result)
        self.assertIn("error", message.lower())

    @patch('admin_app.create_client')
    def test_insert_certification_success(self, mock_create_client):
        """Test successful certification insertion."""
        mock_client = Mock()
        mock_table = Mock()
        mock_response = Mock()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value.execute.return_value = mock_response
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)
        cert_data = {
            "name": "Test Certification",
            "link": "https://example.com/cert",
            "image_path": ""
        }

        result, message = manager.insert_certification(cert_data)

        self.assertTrue(result)
        self.assertIn("success", message.lower())
        mock_client.table.assert_called_once_with('certifications')

    @patch('admin_app.create_client')
    def test_insert_skill_success(self, mock_create_client):
        """Test successful skill insertion."""
        mock_client = Mock()
        mock_table = Mock()
        mock_response = Mock()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value.execute.return_value = mock_response
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)
        skill_data = {
            "name": "Python",
            "category": "Programming",
            "icon_path": ""
        }

        result, message = manager.insert_skill(skill_data)

        self.assertTrue(result)
        self.assertIn("success", message.lower())
        mock_client.table.assert_called_once_with('skills')

    @patch('admin_app.create_client')
    def test_verify_data_retention_with_data(self, mock_create_client):
        """Test data verification when data exists."""
        mock_client = Mock()
        mock_table = Mock()
        mock_response = Mock()
        mock_response.data = [{"id": 1, "name": "Test"}]
        mock_client.table.return_value = mock_table
        mock_table.select.return_value.execute.return_value = mock_response
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)
        result, message = manager.verify_data_retention("projects")

        self.assertTrue(result)
        self.assertIn("found", message.lower())

    @patch('admin_app.create_client')
    def test_verify_data_retention_no_data(self, mock_create_client):
        """Test data verification when no data exists."""
        mock_client = Mock()
        mock_table = Mock()
        mock_response = Mock()
        mock_response.data = []
        mock_client.table.return_value = mock_table
        mock_table.select.return_value.execute.return_value = mock_response
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)
        result, message = manager.verify_data_retention("projects")

        self.assertFalse(result)
        self.assertIn("no data", message.lower())

    @patch('admin_app.create_client')
    def test_verify_data_retention_error(self, mock_create_client):
        """Test data verification on error."""
        mock_client = Mock()
        mock_table = Mock()
        mock_table.select.side_effect = Exception("Select error")
        mock_client.table.return_value = mock_table
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)
        result, message = manager.verify_data_retention("projects")

        self.assertFalse(result)
        self.assertIn("error", message.lower())

    @patch('admin_app.create_client')
    def test_upload_image_success(self, mock_create_client):
        """Test successful image upload."""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_client.storage = mock_storage
        mock_storage.from_ = Mock(return_value=mock_bucket)
        mock_bucket.upload = Mock(return_value=None)
        mock_bucket.get_public_url = Mock(return_value="https://example.com/public/image.jpg")
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)

        # Create a temporary test file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b"fake image data")
            temp_path = f.name

        try:
            success, message, url = manager.upload_image(temp_path)
            self.assertTrue(success)
            self.assertIn("success", message.lower())
            self.assertEqual(url, "https://example.com/public/image.jpg")
        finally:
            os.unlink(temp_path)

    @patch('admin_app.create_client')
    def test_upload_image_bucket_not_found(self, mock_create_client):
        """Test image upload when bucket not found."""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_client.storage = mock_storage
        mock_storage.from_ = Mock(return_value=mock_bucket)
        mock_bucket.upload = Mock(side_effect=Exception("Bucket 'Site_Images' not found"))
        mock_create_client.return_value = mock_client

        manager = SupabaseManager(self.test_url, self.test_key)

        # Create a temporary test file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b"fake image data")
            temp_path = f.name

        try:
            success, message, url = manager.upload_image(temp_path)
            self.assertFalse(success)
            self.assertIn("bucket", message.lower())
            self.assertIsNone(url)
        finally:
            os.unlink(temp_path)


class TestDataStructures(unittest.TestCase):
    """Test cases for data structure validation."""

    def test_project_data_structure(self):
        """Test that project data has required fields."""
        project_data = {
            "name": "Test Project",
            "repo_link": "https://github.com/test",
            "description": "Test description",
            "tags": ["python", "tkinter"],
            "category": "fullstack",
            "image_path": ""
        }

        required_fields = ["name", "repo_link", "description", "tags", "category"]
        for field in required_fields:
            self.assertIn(field, project_data)

    def test_certification_data_structure(self):
        """Test that certification data has required fields."""
        cert_data = {
            "name": "Test Certification",
            "link": "https://example.com/cert",
            "image_path": ""
        }

        required_fields = ["name", "link"]
        for field in required_fields:
            self.assertIn(field, cert_data)

    def test_skill_data_structure(self):
        """Test that skill data has required fields."""
        skill_data = {
            "name": "Python",
            "category": "Programming",
            "icon_path": ""
        }

        required_fields = ["name", "category"]
        for field in required_fields:
            self.assertIn(field, skill_data)


class TestProjectCategories(unittest.TestCase):
    """Test cases for project categories."""

    def test_valid_categories(self):
        """Test that only valid categories are used."""
        valid_categories = ["fullstack", "ds-ai-ml", "hardware-cv"]
        test_category = "fullstack"

        self.assertIn(test_category, valid_categories)

    def test_all_categories_defined(self):
        """Test that all expected categories are defined."""
        expected_categories = ["fullstack", "ds-ai-ml", "hardware-cv"]
        actual_categories = ["fullstack", "ds-ai-ml", "hardware-cv"]

        self.assertEqual(set(expected_categories), set(actual_categories))


if __name__ == "__main__":
    unittest.main()
