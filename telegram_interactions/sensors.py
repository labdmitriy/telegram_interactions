from typing import Union, Dict, List

from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

from .bot import TelegramBot


class TelegramActionsIncrementSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(self, token: str, allowed_updates: Union[List, None] = None,
                 answer_text: str = '',
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.telegram_bot = TelegramBot(token)
        self.message_state = self.telegram_bot._load_message_state()
        self.allowed_updates = allowed_updates
        self.answer_text = answer_text

    def _get_message_id(self, update: Dict) -> int:
        return update['callback_query']['message']['message_id']

    def poke(self, context: Dict) -> bool:
        offset = self.message_state['offset']
        updates = self.telegram_bot.get_updates(
            offset=offset,
            timeout=3,
            allowed_updates=self.allowed_updates
        )

        result = updates['result']
        message_id = self.message_state['message_id']
        message_update = [update for update in result
                          if self._get_message_id(update) == message_id]
        print(message_update)

        if len(message_update) > 0:
            callback_query = message_update[0]['callback_query']
            chat_id = callback_query['message']['chat']['id']

            reply_markup: Dict = {'inline_keyboard': [[]]}
            self.telegram_bot.edit_message(chat_id, message_id,
                                           reply_markup, self.answer_text)

            callback_query_id = callback_query['id']
            self.telegram_bot.answer_callback(callback_query_id)
            self.telegram_bot.save_callback_query(callback_query)

            return True

        return False
