API_ENDPOINT = 'status'

class StatusApi:
    """Helper class to interact with the Beekeeper Status API
    """
    def __init__(self, sdk):
        self.sdk = sdk

    def get_status(
            self,
    ) -> 'Status':
        """Retrieve status of authenticated user

        The first `limit` users in alphabetical order are returned, after list offset `offset`.
        :return Status object
        """
        response = self.sdk.api_client.get(API_ENDPOINT)
        return Status(self.sdk, raw_data=response)

class Status:
    """Representation of user status"""
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_notifications(self) -> int:
        """Returns the number of unread notifications"""
        return int(self._raw.get('notifications'))

    def get_unread_messages(self) -> int:
        """Returns the number of unread messages"""
        return self._raw.get('unread_messages')

