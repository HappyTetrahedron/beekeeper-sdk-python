import beekeeper_sdk
__version__ = beekeeper_sdk.__version__
del beekeeper_sdk

from .beekeeper_chat_bot import BeekeeperChatBot
from .handlers import RegexHandler, CommandHandler, MessageHandler

