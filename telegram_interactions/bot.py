import json
from typing import Union, Dict, List
from operator import itemgetter
from datetime import datetime

import requests


class TelegramBot:
    BASE_URL = 'https://api.telegram.org'

    def __init__(
        self,
        token: str,
        state_file_path: str = '/tmp/message_state.json',
        callback_file_path: str = '/tmp/callback_data.json'
    ) -> None:
        self.token = token
        self.base_url = f'{self.BASE_URL}/bot{token}'
        self.state_file_path = state_file_path
        self.callback_file_path = callback_file_path

    def _save_message_state(self, message_id: int) -> None:
        get_update_id = itemgetter('update_id')
        current_updates = self.get_updates()

        print('current update', current_updates)
        update_ids = list(map(get_update_id, current_updates['result']))

        if len(update_ids) > 0:
            offset = max(update_ids) + 1
        else:
            offset = 0

        print('offset', offset)

        message_state = {}
        message_state['message_id'] = message_id
        message_state['offset'] = offset

        with open(self.state_file_path, 'w') as f:
            f.write(json.dumps(message_state))

    def _load_message_state(self) -> Dict:
        try:
            with open(self.state_file_path, 'r') as f:
                message_state = json.loads(f.read())
        except FileNotFoundError:
            message_state = {}
            message_state['message_id'] = 0
            message_state['offset'] = 0

        return message_state

    def save_callback_query(self, callback_query: Dict) -> None:
        callback_query['timestamp'] = datetime.now().isoformat()
        with open(self.callback_file_path, 'w') as f:
            f.write(json.dumps(callback_query))

    def load_callback_query(self) -> Dict:
        with open(self.callback_file_path, 'r') as f:
            callback_query = json.loads(f.read())
        return callback_query

    def send_message(
        self,
        chat_id: Union[str, int],
        message_text: str,
        include_button: bool = False,
        button_text: str = '',
        reporter_name: str = '',
        parse_mode: str = 'Markdown',
        disable_notification: bool = True,
    ) -> Dict:

        payload: Dict = {
            'chat_id': chat_id,
            'text': message_text,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification
        }

        if include_button:
            go_button = {
                'text': button_text,
                'callback_data': reporter_name
            }
            go_keyboard = {'inline_keyboard': [[go_button]]}
            payload['reply_markup'] = go_keyboard

        response = requests.post(
            f'{self.base_url}/sendMessage', json=payload, timeout=5
        )
        print(response)

        message_info = response.json()
        message_id = message_info['result']['message_id']
        self._save_message_state(message_id)

        return response.json()

    def get_updates(self, offset: int = 0, timeout: int = 0,
                    allowed_updates: Union[List, None] = None) -> Dict:
        payload: Dict = {
            'timeout': timeout,
            'offset': offset,
        }

        if allowed_updates is None:
            payload['allowed_updates'] = json.dumps([])
        else:
            payload['allowed_updates'] = json.dumps(allowed_updates)

        print('payload', payload)

        response = requests.post(
            f'{self.base_url}/getUpdates', json=payload, timeout=5
        )
        return response.json()

    def answer_callback(self, callback_query_id: str) -> Dict:
        payload: Dict = {
            'callback_query_id': callback_query_id
        }
        response = requests.post(
            f'{self.base_url}/answerCallbackQuery', json=payload, timeout=5
        )
        return response.json()

    def edit_message(self, chat_id: str, message_id: str,
                     reply_markup: Dict, message_text: str = '') -> Dict:
        payload: Dict = {
            'chat_id': chat_id,
            'message_id': message_id,
            'reply_markup': reply_markup
        }

        if message_text:
            payload['text'] = message_text

        response = requests.post(
            f'{self.base_url}/editMessageText', json=payload, timeout=5
        )
        return response.json()
