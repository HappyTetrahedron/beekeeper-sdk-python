from beekeeper_sdk.iterators import BeekeeperApiLimitOffsetIterator

API_ENDPOINT = 'profiles'


class ProfileApi:
    def __init__(self, sdk):
        self.sdk = sdk

    def get_profiles(
            self,
            q=None,
            include_bots=None,
            limit=None,
            offset=None,
    ):
        query = {}
        if q is not None:
            query['q'] = q
        if include_bots is not None:
            query['include_bots'] = include_bots
        if limit:
            query['limit'] = limit
        if offset is not None:
            query['offset'] = offset
        response = self.sdk.api_client.get(API_ENDPOINT, query=query)
        return [Profile(self.sdk, raw_data=user) for user in response]

    def get_profiles_iterator(self, include_bots=None):
        def call(offset=None, limit=None):
            return self.get_profiles(include_bots=include_bots, offset=offset, limit=limit)
        return BeekeeperApiLimitOffsetIterator(call)

    def get_profile(self, user_id, include_totals=False):
        query = {
            'include_activities': False,
            'include_totals': include_totals,
        }
        response = self.sdk.api_client.get(API_ENDPOINT, user_id, query=query)
        return Profile(self.sdk, raw_data=response.get('user'))

    def get_profile_by_username(self, username, include_totals=False):
        return self.get_profile(username, include_totals=include_totals)


class Profile:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_id(self):
        return self._raw.get('id')

    def get_display_name(self):
        return self._raw.get('display_name')

    def get_is_bot(self):
        return self._raw.get('is_bot')

    def get_profile(self):
        return self._raw.get('profile')

    def get_firstname(self):
        return self._raw.get('firstname')

    def get_lastname(self):
        return self._raw.get('lastname')

    def get_role(self):
        return self._raw.get('role')

    def get_name(self):
        return self._raw.get('name')

    def get_avatar(self):
        return self._raw.get('avatar')
