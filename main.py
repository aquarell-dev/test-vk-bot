import os
from services.photo_service import PhotoService
from services.vk_service import VkService
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get('TOKEN', None)

def main():
    VkService(
        token,
        PhotoService()
    ).start()

if __name__ == '__main__':
    main()
