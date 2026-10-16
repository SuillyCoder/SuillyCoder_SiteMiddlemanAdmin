"""
Build script for PortfolioAdmin with excluded heavy dependencies.
This creates a much smaller executable by excluding ML libraries that are not needed.
"""
import subprocess
import sys
import os

def build():
    """Build the executable with exclusions."""
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Warning: .env file not found. Please create it with your Supabase credentials.")
        print("The application will still work, but you'll need to enter credentials manually.")

    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'PortfolioAdmin',
        '--add-data', '.env;.' if os.name == 'nt' else '.env:.',
        '--exclude-module', 'torch',
        '--exclude-module', 'tensorflow',
        '--exclude-module', 'keras',
        '--exclude-module', 'scipy',
        '--exclude-module', 'pandas',
        '--exclude-module', 'numpy',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'sklearn',
        '--exclude-module', 'IPython',
        '--exclude-module', 'jedi',
        '--exclude-module', 'parso',
        '--exclude-module', 'sympy',
        '--exclude-module', 'numba',
        '--exclude-module', 'llvmlite',
        '--exclude-module', 'onnxruntime',
        '--exclude-module', 'transformers',
        '--exclude-module', 'nltk',
        '--exclude-module', 'h5py',
        '--exclude-module', 'grpc',
        '--exclude-module', 'PySide6',
        '--exclude-module', 'shiboken6',
        'admin_app.py'
    ]

    print("Building PortfolioAdmin with excluded heavy dependencies...")
    print("This will create a much smaller executable.")
    print()

    try:
        subprocess.run(cmd, check=True)
        print("\nBuild complete! Executable is in the 'dist' folder.")
        print("\nNote: The .env file is bundled with the executable.")
        print("Place the executable and .env file in the same directory to use auto-connect.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
