import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Create media directories
media_dirs = [
    'media',
    'media/users',
    'media/courses',
    'media/courses/thumbnails',
    'media/lessons',
    'media/lessons/attachments',
    'media/lessons/resources',
    'media/certificates',
    'media/certificates/pdfs',
    'media/certificates/qrcodes',
    'media/content',
    'media/content/media',
    'logs',
    'staticfiles',
    'static',
]

for dir_path in media_dirs:
    full_path = BASE_DIR / dir_path
    full_path.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {full_path}")

# Create .gitkeep files to track empty directories
gitkeep_dirs = [
    'media',
    'logs',
    'staticfiles',
    'static',
]

for dir_path in gitkeep_dirs:
    gitkeep_path = BASE_DIR / dir_path / '.gitkeep'
    gitkeep_path.touch(exist_ok=True)
    print(f"Created .gitkeep in: {dir_path}")