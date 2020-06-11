import base64

from beekeeper_sdk.users import User
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from beekeeper_sdk import BeekeeperSDK
from .beekeeper_message_listener import BeekeeperMessageListener
from .decrypter import Decrypter

CONFIG_API_ENDPOINT = "config/client"


class BeekeeperChatBot:
    def __init__(self, tenant_url, api_token):
        super().__init__()
        self.sdk = BeekeeperSDK(tenant_url=tenant_url, api_token=api_token)
        self.user = None
        self._pubnub = None
        self._handlers = []

    def start(self):
        """Start this chat bot
        The chat bot will start listening for incoming chat messages on a separate thread.
        """
        config = self.sdk.api_client.get(CONFIG_API_ENDPOINT)
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

    def add_handler(self, handler):
        """Add a handler to this bot which can handle messages received by it
        :param handler: A handler object (has to implement AbstractHandler)"""
        if handler not in self._handlers:
            self._handlers.append(handler)

    def remove_handler(self, handler):
        """Remove a handler from this bot
        :param handler: A handler object"""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def stop(self):
        """Stop this chat bot (blocking)
        """
        self._pubnub.unsubscribe_all().execute()

    def _on_message(self, message):
        for handler in self._handlers:
            if handler.matches(message):
                handler.handle(self, message)
                return
