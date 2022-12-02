from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = os.path.join(BASE_DIR, "static")

def save_photo(photo, file_name):
    photo_ext = photo.name.split('.')[-1]
    photo_path = os.path.join("menu_pics", str(file_name)+'.'+photo_ext)
    photo_abs_path = os.path.join(STATIC_DIR, photo_path)
    photo_file = open(photo_abs_path, 'wb')

    for chunk in photo.chunks():
        photo_file.write(chunk)
    photo_file.close()
    # save it in database
    return photo_path
