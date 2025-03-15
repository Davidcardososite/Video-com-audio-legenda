# utils.py
from moviepy.config import change_settings
from word2number import w2n
import os

def check_create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def configure_moviepy():
    imagemagick_path = os.getenv('IMAGEMAGICK_BINARY', r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe")
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
