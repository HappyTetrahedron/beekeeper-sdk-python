import requests

from . import __version__
from .conversations.conversations import ConversationApi
from .files.files import FileApi
from .streams.streams import StreamApi
from .profiles.profiles import ProfileApi
from .users.users import UserApi


class BeekeeperSDK:

    API_BASE_PATH = "/api/2/"

    def __init__(self, tenant_url, api_token):
        # TODO  validate arguments
        self.tenant_url = tenant_url
        self.api_token = api_token
        self.conversations = ConversationApi(self)
        self.files = FileApi(self)
        self.streams = StreamApi(self)
        self.profiles = ProfileApi(self)
        self.users = UserApi(self)

        self.headers = {
            "Authorization": "Token {}".format(self.api_token),
            "User-Agent": "BeekeeperSDK-Python/{}".format(__version__)
        }

    def get(self, *path, base_path=API_BASE_PATH, query=None):
        endpoint = "/".join([str(it) for it in path])
        response = requests.get(
            "{}{}{}".format(self.tenant_url, base_path, endpoint),
            headers=self.headers,
            params=query
        )
        json = response.json()
        if "error" in json:
            raise BeekeeperApiException(json["error"])
        return json

    def delete(self, *path, base_path=API_BASE_PATH):
        endpoint = "/".join([str(it) for it in path])
        response = requests.delete(
            "{}{}{}".format(self.tenant_url, base_path, endpoint),
            headers=self.headers,
        )
        json = response.json()
        if "error" in json:
            raise BeekeeperApiException(json["error"])
        return json

    def post(self, *path, payload=None, base_path=API_BASE_PATH):
        payload = payload or {}
        endpoint = "/".join([str(it) for it in path])
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers)
        response = requests.post(
            "{}{}{}".format(self.tenant_url, base_path, endpoint),
            json=payload,
            headers=headers,
        )
        json = response.json()
        if "error" in json:
            raise BeekeeperApiException(json["error"])
        return json

    def put(self, *path, payload=None, base_path=API_BASE_PATH):
        payload = payload or {}
        endpoint = "/".join([str(it) for it in path])
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers)
        response = requests.put(
            "{}{}{}".format(self.tenant_url, base_path, endpoint),
            json=payload,
            headers=headers,
        )
        json = response.json()
        if "error" in json:
            raise BeekeeperApiException(json["error"])
        return json

    def follow_redirect(self, url):
        response = requests.head(url, headers=self.headers)
        return response.headers.get("Location")


class BeekeeperApiException(Exception):
    pass
