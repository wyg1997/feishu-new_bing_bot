import time
from typing import List, Union
import logging
from abc import ABC, abstractmethod

from core.data_structure import MsgInfo, ActionType
from handlers import bot_register


class BotBase(ABC):
    def __init__(self, chat_id):
        self._chat_id = chat_id
        self._timestamp = time.time()
        self._message_ids = set()

    def __del__(self):
        logging.info(f"Bot {self.chat_id} is deleted")

    @property
    def chat_id(self):
        return self.chat_id

    @property
    def message_ids(self):
        return self._message_ids

    def is_timeout(self, timeout):
        raise NotImplementedError("is_timeout not implemented yet")

    def do(self, msg_info: MsgInfo):
        self._message_ids.add(msg_info.msg_id)
        self._update_timestamp()
        self._do(msg_info)

    def _update_timestamp(self):
        self.timestamp = time.time()

    @abstractmethod
    def _do(self, msg_info: MsgInfo):
        """
        Implement this method to do the bot action.
        """
        raise NotImplementedError("_do not implemented yet")


class BotPool(object):
    def __init__(self, bot_count):
        self.bot_count = bot_count
        self.bots: List[Union[None, BotBase]] = [None] * bot_count
        self.chat_id2bot_idx = {}

    def __contains__(self, chat_id):
        return chat_id in self.chat_id2bot_idx

    def __getitem__(self, chat_id):
        assert chat_id in self.chat_id2bot_idx, f"chat_id: {chat_id} not in pool"
        return self.bots[self.chat_id2bot_idx[chat_id]]

    def ask(self, msg_info: MsgInfo, action_type: ActionType):
        if msg_info.chat_id not in self:
            self._create_bot(msg_info.chat_id, action_type)

        bot = self[msg_info.chat_id]
        assert bot is not None, "Unexpected error: bot is None"

        bot.do(msg_info)
        logging.info(f"Bot pool current size: {sum(x is not None for x in self.bots)}")

    def try_free_bots(self):
        # TODO: free bots which are timeout
        for i in range(self.bot_count):
            bot = self.bots[i]
            if bot is not None:
                self.bots[i] = None
                del bot
        self.chat_id2bot_idx = {}

    def _create_bot(self, chat_id, action_type):
        assert (
            chat_id not in self.chat_id2bot_idx
        ), f"chat_id: {chat_id} already in pool"
        if all(x is not None for x in self.bots):
            self.try_free_bots()
        for i in range(self.bot_count):
            if self.bots[i] is None:
                # TODO: read cookie path from config
                self.bots[i] = bot_register.get(action_type)(chat_id)
                self.chat_id2bot_idx[chat_id] = i
                return self.bots[i]
        raise RuntimeError("Don't have enough space to create new bot")


# TODO: load bot count from config
bot_pool = BotPool(bot_count=10)
