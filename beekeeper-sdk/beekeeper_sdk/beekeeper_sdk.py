from .client import BeekeeperApiClient
from .conversations.conversations import ConversationApi
from .files.files import FileApi
from .profiles.profiles import ProfileApi
from .streams.streams import StreamApi
from .users.users import UserApi


class BeekeeperSDK:

    def __init__(self, tenant_url, api_token):
        # TODO  validate arguments
        self.api_client = BeekeeperApiClient(tenant_url, api_token)
        self.conversations = ConversationApi(self)
        self.files = FileApi(self)
        self.streams = StreamApi(self)
        self.profiles = ProfileApi(self)
        self.users = UserApi(self)
