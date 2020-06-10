from typing import Union, Dict
from collections import defaultdict

import requests

from airflow.operators import BaseOperator
from airflow.utils.decorators import apply_defaults

from .bot import TelegramBot


class TelegramSendMessageOperator(BaseOperator):
    @apply_defaults
    def __init__(self, token: str, chat_id: Union[str, int], message_text: str,
                 include_button: bool, button_text: str, reporter_name: str,
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.telegram_bot = TelegramBot(token)
        self.chat_id = chat_id
        self.message_text = message_text
        self.include_button = include_button
        self.button_text = button_text
        self.reporter_name = reporter_name

    def execute(self, context) -> None:
        message_info = self.telegram_bot.send_message(
            chat_id=self.chat_id,
            message_text=self.message_text,
            include_button=self.include_button,
            button_text=self.button_text,
            reporter_name=self.reporter_name
        )
        print(message_info)
        return


class TelegramEventSaveOperator(BaseOperator):
    @apply_defaults
    def __init__(self, token: str, airtable_url: str, airtable_api_key: str,
                 event_type: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.telegram_bot = TelegramBot(token)
        self.airtable_url = airtable_url
        self.airtable_api_key = airtable_api_key
        self.event_type = event_type

    def _generate_db_record(self, callback_query: Dict) -> Dict:
        data: Dict[str, Dict] = defaultdict(dict)
        fields = {
            'chat_id': str(callback_query['message']['chat']['id']),
            'username': str(callback_query['from']['username']),
            'triggered_at': callback_query['timestamp'],
            'event_type': self.event_type,
            'reporter_name': callback_query['data']
        }

        data['fields'] = fields

        db_record: Dict = {}
        db_record['records'] = []
        db_record['records'].append(dict(data))
        print(db_record)

        return db_record

    def _save_db_record(self, db_record: Dict) -> None:
        headers = {
            'Authorization': f'Bearer {self.airtable_api_key}'
        }

        requests.post(self.airtable_url, json=db_record, headers=headers)

    def execute(self, context) -> None:
        callback_query = self.telegram_bot.load_callback_query()
        db_record = self._generate_db_record(callback_query)
        self._save_db_record(db_record)
