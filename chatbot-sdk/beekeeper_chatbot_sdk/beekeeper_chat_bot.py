import base64
from abc import ABC
from abc import abstractmethod

from beekeeper_sdk.users import User
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from beekeeper_sdk import BeekeeperSDK
from .beekeeper_message_listener import BeekeeperMessageListener
from .decrypter import Decrypter

CONFIG_API_ENDPOINT = "config/client"


class BeekeeperChatBot(ABC):
    def __init__(self, tenant_url, api_token):
        super().__init__()
        self.sdk = BeekeeperSDK(tenant_url=tenant_url, api_token=api_token)
        self.user = None
        self._pubnub = None

    def start(self):
        config = self.sdk.get(CONFIG_API_ENDPOINT)
        self.user = User(self.sdk, config.get('user'))

        pubnub_subscribe_key = config.get('tenant').get('integrations').get('pubnub').get('subscribe_key')

        pubnub_config = PNConfiguration()
        pubnub_config.subscribe_key = pubnub_subscribe_key
        self._pubnub = PubNub(pubnub_config)

        enc_channel = config.get('enc_channel')
        decrypt = Decrypter(base64.b64decode(enc_channel.get('key')))
        callback = BeekeeperMessageListener(self, decrypt)
        self._pubnub.add_listener(callback)

        self._pubnub.subscribe().channels(enc_channel.get('channel')).execute()

    def stop(self):
        self._pubnub.unsubscribe_all().execute()

    @abstractmethod
    def on_message(self, message):
        pass


def is_valid_message(thing):
    return thing.get('action') == 'create' and thing.get('type') == 'message' and 'data' in thing
