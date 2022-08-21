import sys
import time

from vk_api import VkApi, VkUpload, Captcha
from vk_api.longpoll import Event, VkLongPoll, VkEventType

import requests

from libs.keyboard import default_keyboard
from libs.types import User
from services.photo_service import PhotoService


class VkService:
    def __init__(self, token: str, photo_service: PhotoService) -> None:
        self._token = token
        self._photo_service = photo_service

        self._session = VkApi(token=token, captcha_handler=self._captcha_handler)

        self._upload = VkUpload(self._session)
        self._api = self._session.get_api()

    def __del__(self) -> None:
        print('Bot has been shut down.')

    _api_v = '5.131'

    _greetings = {'Привет бот', 'Начать'}

    def _captcha_handler(self, captcha: Captcha) -> None:
        """
        Sometimes they just be giving you the captcha error and be like go fuck with it on your own,
        well, that's what it's for.
        :param captcha:
        :return:
        """
        key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()

        return captcha.try_again(key)

    def _get_api_vk_url(self, method: str, **params) -> str:
        param_string = '&'.join([f'{key}={value}' for key, value in params.items()])

        return f'https://api.vk.com/method/{method}?{param_string}&access_token={self._token}&v={self._api_v}'

    def _get_user_by_id(self, user_id: int) -> User:
        additional_fields = ['photo_400_orig', 'has_photo']

        user = requests.get(
            self._get_api_vk_url('users.get', user_ids=user_id, fields=','.join(additional_fields))
        ).json()['response'][0]

        return User(
            id=user['id'],
            photo=user['photo_400_orig'],
            has_photo=bool(user['has_photo']),
            name=user['first_name']
        )

    def _message(self, event: Event, message, **kwargs) -> None:
        if event.from_user:
            self._api.messages.send(
                user_id=event.user_id,
                message=message,
                random_id=time.time(),
                **kwargs
            )

    def _greet(self, event: Event) -> None:
        if event.text in self._greetings:
            username = self._get_user_by_id(event.user_id).name
            self._message(event, f'Привет, {username}.', keyboard=default_keyboard.get_keyboard())

    def _send_picture(self, event: Event) -> None:
        if event.text == 'Отправь картинку':
            user = self._get_user_by_id(event.user_id)

            if user.has_photo:
                photo = self._upload.photo_messages(photos=self._photo_service.overlay_picture(user))[0]
                self._message(
                    event,
                    'Вот держи',
                    attachment='photo{}_{}'.format(photo['owner_id'], photo['id'])
                )
            else:
                self._message(event, 'У тебя нет фото.')

            self._message(event, 'Бот выключен')
            sys.exit()

    def start(self) -> None:
        lp = VkLongPoll(self._session)

        print('Successfully logged in. Listening for new events...')

        for event in lp.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                self._greet(event)
                self._send_picture(event)
