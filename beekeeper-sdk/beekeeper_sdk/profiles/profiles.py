from typing import Iterator
from typing import List

from beekeeper_sdk.iterators import BeekeeperApiLimitOffsetIterator

API_ENDPOINT = 'profiles'


class ProfileApi:
    """Helper class to interact with the Beekeeper Profile API
    Beekeeper Profiles are limited representations of Beekeeper Users which are accessible by non-admin accounts.
    """
    def __init__(self, sdk):
        self.sdk = sdk

    def get_profiles(
            self,
            q=None,
            include_bots=None,
            limit=None,
            offset=None,
    ) -> List['Profile']:
        """Retrieve list of profiles from Beekeeper

        The first `limit` profiles in alphabetical order are returned, after list offset `offset`.

        :param q: String query to filter users. Only users whose names contain `q` as a substring are returned.
        :param include_bots: Boolean indicating whether to include Bot profiles in the result
        :param limit: Maximum number of profiles to return
        :param offset: List offset after which to return profiles
        :return List of Profile objects
        """
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

    def get_profiles_iterator(self, include_bots=None) -> Iterator['Profile']:
        """Retrieve list of profiles from Beekeeper

         Returns an iterator over Beekeeper profiles in alphabetical order.

        :param q: String query to filter users. Only users whose names contain `q` as a substring are returned.
        :param include_bots: Boolean indicating whether to include Bot profiles in the result
        :return Iterator of Profile objects
        """
        def call(offset=None, limit=None):
            return self.get_profiles(include_bots=include_bots, offset=offset, limit=limit)
        return BeekeeperApiLimitOffsetIterator(call)

    def get_profile(self, user_id, include_totals=False) -> 'Profile':
        """Retrieve the profile of an user with a given `user_id`
        :param user_id: ID of the user whose profile to retrieve
        :param include_totals: Whether to include information of this user's total Likes, Posts and Comments written
        :return Profile object representing the user
        """
        query = {
            'include_activities': False,
            'include_totals': include_totals,
        }
        response = self.sdk.api_client.get(API_ENDPOINT, user_id, query=query)
        return Profile(self.sdk, raw_data=response.get('user'))

    def get_profile_by_username(self, username, include_totals=False) -> 'Profile':
        """Retrieve the profile of an user with a given `username`
        :param username: ID of the user whose profile to retrieve
        :param include_totals: Whether to include information of this user's total Likes, Posts and Comments written
        :return Profile object representing the user
        """
        return self.get_profile(username, include_totals=include_totals)


class Profile:
    """Representation of a Profile in Beekeeper
    Beekeeper Profiles are limited representations of Beekeeper Users which are accessible by non-admin accounts.
    """
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_id(self) -> str:
        """Returns the ID of the user"""
        return self._raw.get('id')

    def get_display_name(self) -> str:
        """Returns the display name of the user"""
        return self._raw.get('display_name')

    def get_is_bot(self) -> bool:
        """Returns a boolean indicating whether this user is a bot"""
        return self._raw.get('is_bot')

    def get_profile(self) -> str:
        """Returns the username of this user"""
        return self._raw.get('profile')

    def get_firstname(self) -> str:
        """Returns the first name of this user"""
        return self._raw.get('firstname')

    def get_lastname(self) -> str:
        """Returns the last name of this user"""
        return self._raw.get('lastname')

    def get_role(self):
        return self._raw.get('role')

    def get_name(self) -> str:
        """Returns the name of this user"""
        return self._raw.get('name')

    def get_avatar(self) -> str:
        """Returns the Avatar URL of this user"""
        return self._raw.get('avatar')
