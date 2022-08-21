import math
import os, glob
from PIL import Image
import requests

from libs.types import User

default_temp_path = os.path.join(os.getcwd(), 'temp')
default_bg_path = os.path.join(os.getcwd(), 'assets', 'bg.png')

class PhotoService:
    def __init__(self, bg_path: str = default_bg_path, temp_path: str = default_temp_path) -> None:
        self._bg = Image.open(bg_path)
        self._temp_path = temp_path

    def __del__(self) -> None:
        print('Clearing cache...')

        self._clear_temp()

    def _clear_temp(self) -> None:
        path = f'{self._temp_path}/*'

        for file in glob.glob(path):
            os.remove(file)

    def _download_user_avatar(self, user: User) -> str:
        """
        Downloads a photo and puts it into the temp dir.
        :param user:
        :return photo path:
        """
        r = requests.get(user.photo, stream=True)

        path = os.path.join(self._temp_path, f'temp_avatar_{user.id}.png')

        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        return path

    def overlay_picture(self, user: User) -> str:
        """
        Places the user avatar in the centre of the bg picture.
        :param user:
        :return the path of the mod. image:
        """
        avatar_image = Image.open(self._download_user_avatar(user))

        ai_w, ai_h = avatar_image.size
        bg_w, bg_h = self._bg.size

        mod_w = math.ceil((bg_w - ai_w) / 2)
        mod_h = math.ceil((bg_h - ai_h) / 2)

        self._bg.paste(avatar_image, (mod_w, mod_h))

        mod_path = os.path.join(self._temp_path, f'temp_modified_{user.id}.png')

        self._bg.save(mod_path)

        return mod_path
