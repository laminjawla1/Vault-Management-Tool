from flask import current_app
from random import randint
from PIL import Image
import secrets
import os


def save_picture(form_picture):

    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + file_extension
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # resizing the image
    output_size = (150, 150)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_fn

def generate_agent_code():
    return f"YN-{randint(1000, 9999)}"