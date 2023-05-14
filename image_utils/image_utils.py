
import base64
from io import BytesIO
import os
from PIL import Image
import numpy as np


class ImageUtils:

    @staticmethod
    def read_base64_image(base64_string: str) -> Image:
        image_bytes = base64.b64decode(base64_string.split(',')[1])

        # Load the image from bytes
        image = Image.open(BytesIO(image_bytes))

        return image

    @staticmethod
    def save_base64_image(base64_string: str, save_path: str) -> str:
        # Decode the base64 string to bytes
        image_bytes = base64.b64decode(base64_string.split(',')[1])

        # Load the image from bytes
        image = Image.open(BytesIO(image_bytes))

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the image to disk
        image.save(save_path)

        return save_path

    @staticmethod
    def convert_image_to_base64(image: Image.Image) -> str:
        # Resize the image to the desired dimensions
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        resized_image = image.resize((256, 160))

        image_bytes = BytesIO()

        # Save the resized image to the BytesIO in JPEG format with quality 70
        resized_image.save(image_bytes, format="JPEG", quality=70)

        # Reset the BytesIO position to the beginning
        image_bytes.seek(0)

        # Encode the image bytes as Base64
        encoded_image = base64.b64encode(
            image_bytes.getvalue()).decode("utf-8")

        return encoded_image

    @staticmethod
    def image_to_grayscale(image: Image.Image) -> Image.Image:
        return image.convert('L')
