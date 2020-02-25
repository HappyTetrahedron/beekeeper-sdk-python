import requests

from .exceptions import BeekeeperApiException
from . import __version__


def raise_for_status(response):
    if response.status_code == 200:
        return
    if response.status_code == 401:
        raise BeekeeperApiException("Invalid token")
    if response.status_code == 403:
        raise BeekeeperApiException("Access denied")
    if response.status_code == 404:
        raise BeekeeperApiException("Not found")
    raise BeekeeperApiException("Unexpected error: {}".format(response.status_code))


class BeekeeperApiClient:

    API_BASE_PATH = "/api/2/"

    def __init__(self, tenant_url, api_token):
        self.tenant_url = tenant_url
        self.api_token = api_token
        self.headers = {
            "Authorization": "Token {}".format(self.api_token),
            "User-Agent": "BeekeeperSDK-Python/{}".format(__version__)
        }

    def _request(self, method, path, base_path, query=None, payload=None):
        headers = dict()
        headers.update(self.headers)

        if payload:
            headers["Content-Type"] = "application/json"
        endpoint = "/".join([str(it) for it in path])
        response = requests.request(
            method,
            "{}{}{}".format(self.tenant_url, base_path, endpoint),
            headers=self.headers,
            json=payload,
            params=query,
        )
        json = response.json()
        if json and "error" in json:
            raise BeekeeperApiException(json["error"])
        raise_for_status(response)
        return json

    def get(self, *path, base_path=API_BASE_PATH, query=None):
        return self._request('get', path, base_path, query=query)

    def delete(self, *path, base_path=API_BASE_PATH):
        return self._request('delete', path, base_path)

    def post(self, *path, payload=None, base_path=API_BASE_PATH):
        return self._request('post', path, base_path, payload=payload or {})

    def put(self, *path, payload=None, base_path=API_BASE_PATH):
        return self._request('put', path, base_path, payload=payload or {})

    def get_redirect_url(self, url):
        response = requests.head(url, headers=self.headers)
        return response.headers.get("Location")
