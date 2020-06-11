import re
from abc import ABC
from abc import abstractmethod

from beekeeper_sdk.conversations import MESSAGE_TYPE_REGULAR


class AbstractHandler(ABC):

    @abstractmethod
    def matches(self, message) -> bool:
        """Should return true if this handler feels responsible for handling `message`, false otherwise
        :param message: beekeeper_sdk.conversations.ConversationMessage object
        :return Whether or not this handler wants to handle `message`"""
        pass

    @abstractmethod
    def handle(self, bot, message):
        """Handles a message received by `bot`
        :param bot: BeekeeperChatBot
        :param message: beekeeper_sdk.conversations.ConversationMessage object"""
        pass


class CommandHandler(AbstractHandler):
    """A handler that responds to slash commands of the form `/command`"""
    def __init__(self, command, callback_function, message_types=None):
        """
        :param command: The command this handler should respond to (not including the preceding slash)
        :param callback_function: The function to call when a matching message is received.
        The callback function is passed the BeekeeperChatBot and beekeeper_sdk.conversations.ConversationMessage as arguments
        :param message_types: List of message types this handler should consider.
        """
        self.message_types = message_types or [MESSAGE_TYPE_REGULAR]
        self.command = command
        self.callback_function = callback_function

    def matches(self, message) -> bool:
        if message.get_type() in self.message_types:
            if message.get_text():
                if message.get_text().startswith("/{}".format(self.command)):
                    return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)


class RegexHandler(AbstractHandler):
    """A handler that responds to messages matching a RegExp"""
    def __init__(self, regex, callback_function, message_types=None):
        """
        :param regex: A regular expression that matches the message texts this handler should respond to.
        :param callback_function: The function to call when a matching message is received.
        The callback function is passed the BeekeeperChatBot and beekeeper_sdk.conversations.ConversationMessage as arguments
        :param message_types: List of message types this handler should consider.
        """
        self.message_types = message_types or [MESSAGE_TYPE_REGULAR]
        self.regex = re.compile(regex)
        self.callback_function = callback_function

    def matches(self, message) -> bool:
        if message.get_type() in self.message_types:
            if message.get_text():
                if self.regex.search(message.get_text()):
                    return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)


class MessageHandler(AbstractHandler):
    """A handler that responds to all messages"""
    def __init__(self, callback_function, message_types=None):
        """
        :param callback_function: The function to call when a matching message is received.
        The callback function is passed the BeekeeperChatBot and beekeeper_sdk.conversations.ConversationMessage as arguments
        :param message_types: List of message types this handler should consider.
        """
        self.message_types = message_types or [MESSAGE_TYPE_REGULAR]
        self.callback_function = callback_function

    def matches(self, message) -> bool:
        if message.get_type() in self.message_types:
            return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)
