from beekeepersdk.users import User

API_ENDPOINT = "profiles"


def get_profiles(
        sdk,
        q=None,
        include_bots=None,
        limit=None,
        offset=None,
):
    query = {}
    if q is not None:
        query["q"] = q
    if include_bots is not None:
        query["include_bots"] = include_bots
    if limit:
        query["limit"] = limit
    if offset is not None:
        query["offset"] = offset
    response = sdk.get(API_ENDPOINT, query=query)
    return [Profile(raw_data=user) for user in response]


def get_profile(sdk, user_id, include_activities=False, include_totals=False):
    query = {
        "include_activities": include_activities,
        "include_totals": include_totals
    }
    response = sdk.get(API_ENDPOINT, user_id, query=query)
    return ProfileWrapper(raw_data=response)


def get_profile_by_username(sdk, username, include_activities=False, include_totals=False):
    return get_profile(sdk, username, include_totals=include_totals, include_activities=include_activities)


def get_user_by_tenantuserid(sdk, tenantuserid):
    response = sdk.get(API_ENDPOINT, "by_tenant_user_id", tenantuserid)
    return User(raw_data=response)


def delete_user(sdk, user_id):
    response = sdk.delete(API_ENDPOINT, user_id)
    return response.get("status") == "OK"


class ProfileWrapper:
    def __init__(self, raw_data=None):
        self._raw = raw_data or {}

    def get_user(self):
        #TODO I think this is different from the User object
        return User(raw_data=self._raw.get("user"))
    #TODO activities


class Profile:
    def __init__(self, raw_data=None):
        self._raw = raw_data or {}

    def get_id(self):
        return self._raw.get("id")

    def get_display_name(self):
        return self._raw.get("display_name")

    def get_is_bot(self):
        return self._raw.get("is_bot")

    def get_profile(self):
        return self._raw.get("profile")

    def get_firstname(self):
        return self._raw.get("firstname")

    def get_lastname(self):
        return self._raw.get("lastname")

    def get_role(self):
        return self._raw.get("role")

    def get_name(self):
        return self._raw.get("name")

    def get_avatar(self):
        return self._raw.get("avatar")
