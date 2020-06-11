from typing import Iterator
from typing import List

from beekeeper_sdk.iterators import BeekeeperApiLimitOffsetIterator

API_ENDPOINT = 'users'

USER_ROLE_MEMBER = 'member'
USER_ROLE_ADMIN = 'admin'

CUSTOM_FIELD_TYPE_TEXT = 'text'
CUSTOM_FIELD_TYPE_NUMBER = 'number'
CUSTOM_FIELD_TYPE_DATE = 'date'
CUSTOM_FIELD_TYPE_DROPDOWN = 'dropdown'
CUSTOM_FIELD_TYPE_TEXTAREA = 'textarea'
CUSTOM_FIELD_TYPE_PHONE = 'phone'
CUSTOM_FIELD_TYPE_EMAIL = 'email'

USER_GENDER_MALE = 'male'
USER_GENDER_FEMALE = 'female'

USER_SORT_ASCENDING = 'asc'
USER_SORT_DESCENDING = 'desc'


class UserApi:
    """Helper class to interact with the Beekeeper User API
    The Beekeeper User API requires administrator privileges to use.
    """
    def __init__(self, sdk):
        self.sdk = sdk

    def get_users(
            self,
            sort=None,
            q=None,
            include_bots=None,
            limit=None,
            offset=None,
            include_self=None,
            exclude_users_which_never_logged_in=None,
    ) -> List['User']:
        """Retrieve list of users from Beekeeper

        The first `limit` users in alphabetical order are returned, after list offset `offset`.

        :param sort: Sorting order, one of `USER_SORT_ASCENDING`, `USER_SORT_DESCENDING`
        :param q: String query to filter users. Only users whose names contain `q` as a substring are returned.
        :param include_bots: Boolean indicating whether to include Bot users in the result
        :param limit: Maximum number of users to return
        :param offset: List offset after which to return users
        :param include_self: Boolean indicating whether to include the user associated with the BeekeeperSDK in the result
        :param exclude_users_which_never_logged_in: Boolean indicating whether to exclude users that never logged in from the result
        :return List of User objects
        """
        query = {}
        if sort is not None:
            query['sort'] = sort
        if q is not None:
            query['q'] = q
        if include_bots is not None:
            query['include_bots'] = include_bots
        if include_self is not None:
            query['include_self'] = include_self
        if exclude_users_which_never_logged_in is not None:
            query['exclude_users_which_never_logged_in'] = exclude_users_which_never_logged_in
        if limit:
            query['limit'] = limit
        if offset is not None:
            query['offset'] = offset
        response = self.sdk.api_client.get(API_ENDPOINT, query=query)
        return [User(self.sdk, raw_data=user) for user in response]

    def get_users_iterator(
            self,
            sort=None,
            q=None,
            include_bots=None,
            include_self=None,
            exclude_users_which_never_logged_in=None,
    ) -> Iterator['User']:
        """Retrieve list of users from Beekeeper

        Returns an iterator over Beekeeper users in alphabetical order.

        :param sort: Sorting order, one of `USER_SORT_ASCENDING`, `USER_SORT_DESCENDING`
        :param q: String query to filter users. Only users whose names contain `q` as a substring are returned.
        :param include_bots: Boolean indicating whether to include Bot users in the result
        :param include_self: Boolean indicating whether to include the user associated with the BeekeeperSDK in the result
        :param exclude_users_which_never_logged_in: Boolean indicating whether to exclude users that never logged in from the result
        :return Iterator of User objects
        """
        def call(offset=None, limit=None):
            return self.get_users(
                sort=sort,
                include_bots=include_bots,
                include_self=include_self,
                exclude_users_which_never_logged_in=exclude_users_which_never_logged_in,
                offset=offset,
                limit=limit
            )
        return BeekeeperApiLimitOffsetIterator(call)

    def get_user(self, user_id) -> 'User':
        """Retrieve the user with a given `user_id`
        :param user_id: ID of the user
        :return User object representing the user
        """
        response = self.sdk.api_client.get(API_ENDPOINT, user_id)
        return User(self.sdk, raw_data=response)

    def get_user_by_username(self, username) -> 'User':
        """Retrieve the user with a given `username`
        :param username: Username of the user
        :return User object representing the user
        """
        response = self.sdk.api_client.get(API_ENDPOINT, 'by_name', username)
        return User(self.sdk, raw_data=response)

    def get_user_by_tenantuserid(self, tenant_user_id) -> 'User':
        """Retrieve the user with a given `tenant_user_id`
        :param tenant_user_id: ID of the user
        :return User object representing the user
        """
        response = self.sdk.api_client.get(API_ENDPOINT, 'by_tenant_user_id', tenant_user_id)
        return User(self.sdk, raw_data=response)

    def delete_user(self, user_id):
        """Delete the user with ID `user_id`
        :param user_id: ID of the user to delete
        """
        response = self.sdk.api_client.delete(API_ENDPOINT, user_id)
        return response.get('status') == 'OK'


class User:
    """Representation of a User in Beekeeper"""
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_id(self) -> str:
        """Returns the ID of the user"""
        return self._raw.get('id')

    def get_suspended(self) -> bool:
        """Returns a boolean indicating whether this user is suspended"""
        return self._raw.get('suspended')

    def get_display_name(self) -> str:
        """Returns the display name of this user"""
        return self._raw.get('display_name')

    def get_is_bot(self) -> bool:
        """Returns a boolean indicating whether this user is a bot"""
        return self._raw.get('is_bot')

    def get_last_login(self):
        """Returns the timestamp of this user's last login"""
        return self._raw.get('last_login')

    def get_role(self):
        return self._raw.get('role')

    def get_email(self) -> str:
        """Returns the e-mail address of this user"""
        return self._raw.get('email')

    def get_display_name_short(self) -> str:
        """Returns the short display name of this user"""
        return self._raw.get('display_name_short')

    def get_profile(self) -> str:
        """Returns the username of this user"""
        return self._raw.get('profile')

    def get_firstname(self) -> str:
        """Returns the first name of this user"""
        return self._raw.get('firstname')

    def get_lastname(self) -> str:
        """Returns the last name of this user"""
        return self._raw.get('lastname')

    def get_name(self) -> str:
        """Returns the name of this user"""
        return self._raw.get('name')

    def get_language(self):
        """Returns the language spoken by this user"""
        return self._raw.get('language')

    def get_mobile(self):
        """Returns the mobile phone number of this user"""
        return self._raw.get('mobile')

    def get_gender(self):
        """Returns the gender of this user"""
        return self._raw.get('gender')

    def get_avatar(self) -> str:
        """Returns the Avatar URL of this user"""
        return self._raw.get('avatar')

    def get_custom_fields(self) -> List['CustomField']:
        """Returns the list of CustomField objects associated with this user"""
        return [CustomField(self.sdk, raw_data=customfield) for customfield in self._raw.get('custom_fields')]


class CustomField:
    """Representation of a custom profile field of a specific user"""
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_label(self) -> str:
        """Returns the label (name) of the profile field"""
        return self._raw.get('label')

    def get_key(self):
        return self._raw.get('key')

    def get_value(self):
        """Returns the value of this profile field"""
        # TODO there was some weirdness with dropdown fields
        return self._raw.get('value')

    def get_type(self):
        """Returns the type of this profile field"""
        return self._raw.get('type')
