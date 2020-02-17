import base64
import json

from pubnub.callbacks import SubscribeCallback

from beekeeper_sdk.conversations import ConversationMessage


class BeekeeperMessageListener(SubscribeCallback):
    def __init__(self, bot, decrypter, *args, **kwargs):
        self.bot = bot
        self._decrypter = decrypter
        super(BeekeeperMessageListener, self).__init__(*args, **kwargs)

    def status(self, pubnub, status):
        pass

    def presence(self, pubnub, presence):
        pass

    def signal(self, pubnub, signal):
        pass

    def message(self, pubnub, message):
        msg = json.loads(self._decrypter.decrypt(base64.b64decode(message.message)).decode('utf-8'))
        if is_valid_message(msg):
            msg_obj = ConversationMessage(self.bot.sdk, raw_data=msg.get('data'))
            if not self.is_from_current_user(msg_obj):
                self.bot._on_message(msg_obj)

    def is_from_current_user(self, message):
        return message.get_user_id() == self.bot.user.get_id()


def is_valid_message(thing):
    return thing.get('action') == 'create' and thing.get('type') == 'message' and 'data' in thing

