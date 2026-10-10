# Portfolio Admin - Middleman Application

A Python Tkinter-based admin application for managing content on your portfolio website. This application serves as a middleman between your local files and your deployed website, with Supabase integration for data syncing.

## Features

- **Projects Management**: Add projects with name, repository link, description, tags, and category
- **Certifications Management**: Add certifications with name, link, and image
- **Skills Management**: Add skills with name, category, and optional icon
- **Supabase Integration**: Sync data to Supabase for backend storage
- **Data Verification**: Check if data is retained in the database
- **Desktop Application**: Runs as a standalone executable

## Project Categories

The application supports three project categories:
- FullStack
- DS/AI/ML (Data Science, AI, Machine Learning)
- Hardware/CV (Hardware & Computer Vision)

## Requirements

- Python 3.8 or higher
- Required packages (see `requirements.txt`)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/SuillyCoder/SuillyCoder_SiteMiddlemanAdmin.git
cd SuillyCoder_SiteMiddlemanAdmin
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

To run the application directly:

```bash
python admin_app.py
```

### Supabase Setup

1. Create a Supabase project at https://supabase.com
2. Create the following tables in your Supabase database:

**projects table:**
- id (int, primary key)
- name (text)
- repo_link (text)
- description (text)
- tags (array of text)
- category (text)
- image_path (text)
- created_at (timestamp, default: now())

**certifications table:**
- id (int, primary key)
- name (text)
- link (text)
- image_path (text)
- created_at (timestamp, default: now())

**skills table:**
- id (int, primary key)
- name (text)
- category (text)
- icon_path (text)
- created_at (timestamp, default: now())

3. Get your Supabase URL and anon/public key from the Supabase dashboard
4. Enter these credentials in the application's Supabase Configuration section

### Using the Application

1. Launch the application
2. Connect to Supabase by entering your URL and key
3. Click on "Add Project", "Add Certification", or "Add Skill" to open the respective form
4. Fill in the required fields and optionally upload images/icons
5. Click "Submit" to save the data to Supabase
6. Use the "Data Verification" buttons to check if data is retained in the database

## Running Tests

To run the automated tests:

```bash
python test_admin_app.py
```

The tests cover:
- Supabase connection and data operations
- Data structure validation
- Project categories validation

## Creating an Executable

To create a standalone executable (.exe) for Windows, use the provided build script which excludes unnecessary heavy dependencies:

```bash
python build_clean.py
```

This creates a much smaller executable (~37 MB) by excluding ML libraries that are not needed for this application.

Alternatively, you can use PyInstaller directly:

```bash
pyinstaller --onefile --windowed --name "PortfolioAdmin" admin_app.py
```

The executable will be created in the `dist` folder.

### PyInstaller Options

- `--onefile`: Creates a single executable file
- `--windowed`: Runs without a console window (GUI mode)
- `--name`: Sets the name of the executable
- `--exclude-module`: Excludes specific modules (used in build_clean.py to reduce size)

## Project Structure

```
SuillyCoder_SiteMiddlemanAdmin/
├── admin_app.py           # Main application code
├── test_admin_app.py      # Automated tests
├── build_clean.py         # Build script for optimized executable
├── requirements.txt        # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore file
├── build/                # PyInstaller build artifacts
└── dist/                 # Generated executable (after building)
```

## Architecture

The application follows the flow described in the diagrams:

1. **Local Files**: You upload content from your local files through the application
2. **Middleman CRUD Application**: This Python Tkinter app manages the data
3. **Supabase**: Data is synced to Supabase for backend storage
4. **Deployed Website**: Your Next.js portfolio site can fetch data from Supabase

## Data Flow

```
Local Files → Admin App → Supabase → Deployed Website
              ↓
         Data Verification
```

## Troubleshooting

### Supabase Connection Issues

- Ensure your Supabase URL and key are correct
- Check that your Supabase project is active
- Verify that the required tables exist in your database
- Check Row Level Security (RLS) policies in Supabase

### Image Upload Issues

- Ensure image files are in supported formats (PNG, JPG, JPEG, GIF, WebP)
- Check file paths are accessible
- Verify file sizes are reasonable

### Executable Issues

- Ensure all dependencies are installed before building
- Test the application before creating the executable
- Check antivirus software is not blocking the executable

## License

This project is part of the SuillyCoder portfolio.

## Related Projects

- [SuillyCoder_Site_V3](https://github.com/SuillyCoder/SuillyCoder_Site_V3) - The frontend portfolio website
