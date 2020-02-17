import re

from beekeeper_sdk.conversations import MESSAGE_TYPE_REGULAR


class CommandHandler:
    def __init__(self, command, callback_function, message_types=None):
        self.message_types = message_types or [MESSAGE_TYPE_REGULAR]
        self.command = command
        self.callback_function = callback_function

    def matches(self, message):
        if message.get_type() in self.message_types:
            if message.get_text().startswith("/{}".format(self.command)):
                return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)


class RegexHandler:
    def __init__(self, regex, callback_function, message_types=None):
        self.message_types = message_types or [MESSAGE_TYPE_REGULAR]
        self.regex = re.compile(regex)
        self.callback_function = callback_function

    def matches(self, message):
        if message.get_type() in self.message_types:
            if self.regex.match(message.get_text()):
                return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)


class MessageHandler:
    def __init__(self, callback_function, message_types=None):
        self.message_types = message_types or [MESSAGE_TYPE_REGULAR]
        self.callback_function = callback_function

    def matches(self, message):
        if message.get_type() in self.message_types:
            return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)
