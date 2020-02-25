API_ENDPOINT = "users"

USER_ROLE_MEMBER = "member"
USER_ROLE_ADMIN = "admin"

CUSTOM_FIELD_TYPE_TEXT = "text"
CUSTOM_FIELD_TYPE_NUMBER = "number"
CUSTOM_FIELD_TYPE_DATE = "date"
CUSTOM_FIELD_TYPE_DROPDOWN = "dropdown"
CUSTOM_FIELD_TYPE_TEXTAREA = "textarea"
CUSTOM_FIELD_TYPE_PHONE = "phone"
CUSTOM_FIELD_TYPE_EMAIL = "email"

USER_GENDER_MALE = "male"
USER_GENDER_FEMALE = "female"

USER_SORT_ASCENDING = "asc"
USER_SORT_DESCENDING = "desc"


class UserApi:
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
            exclude_users_which_never_logged_in=None
    ):
        query = {}
        if sort is not None:
            query["sort"] = sort
        if q is not None:
            query["q"] = q
        if include_bots is not None:
            query["include_bots"] = include_bots
        if include_self is not None:
            query["include_self"] = include_self
        if exclude_users_which_never_logged_in is not None:
            query["exclude_users_which_never_logged_in"] = exclude_users_which_never_logged_in
        if limit:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        response = self.sdk.api_client.get(API_ENDPOINT, query=query)
        return [User(self.sdk, raw_data=user) for user in response]

    def get_user(self, user_id):
        response = self.sdk.api_client.get(API_ENDPOINT, user_id)
        return User(self.sdk, raw_data=response)

    def get_user_by_username(self, username):
        response = self.sdk.api_client.get(API_ENDPOINT, "by_name", username)
        return User(self.sdk, raw_data=response)

    def get_user_by_tenantuserid(self, tenantuserid):
        response = self.sdk.api_client.get(API_ENDPOINT, "by_tenant_user_id", tenantuserid)
        return User(self.sdk, raw_data=response)

    def delete_user(self, user_id):
        response = self.sdk.api_client.delete(API_ENDPOINT, user_id)
        return response.get("status") == "OK"


class User:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_id(self):
        return self._raw.get("id")

    def get_suspended(self):
        return self._raw.get("suspended")

    def get_display_name(self):
        return self._raw.get("display_name")

    def get_is_bot(self):
        return self._raw.get("is_bot")

    def get_last_login(self):
        return self._raw.get("last_login")

    def get_role(self):
        return self._raw.get("role")

    def get_email(self):
        return self._raw.get("email")

    def get_display_name_short(self):
        return self._raw.get("display_name_short")

    def get_profile(self):
        return self._raw.get("profile")

    def get_firstname(self):
        return self._raw.get("firstname")

    def get_lastname(self):
        return self._raw.get("lastname")

    def get_name(self):
        return self._raw.get("name")

    def get_language(self):
        return self._raw.get("language")

    def get_mobile(self):
        return self._raw.get("mobile")

    def get_gender(self):
        return self._raw.get("gender")

    def get_avatar(self):
        return self._raw.get("avatar")

    def get_custom_fields(self):
        return [CustomField(self.sdk, raw_data=customfield) for customfield in self._raw.get("custom_fields")]


class CustomField:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_label(self):
        return self._raw.get("label")

    def get_key(self):
        return self._raw.get("key")

    def get_value(self):
        # TODO there was some weirdness with dropdown fields
        return self._raw.get("value")

    def get_type(self):
        return self._raw.get("type")
