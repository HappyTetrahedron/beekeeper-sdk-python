import requests
from xml.etree import ElementTree
import magic
import os


API_ENDPOINT = "files"

FILE_USAGE_TYPE_ATTACHMENT_IMAGE = "attachment_image"
FILE_USAGE_TYPE_ATTACHMENT_FILE = "attachment_file"
FILE_USAGE_TYPE_COVER_IMAGE = "cover_image"
FILE_USAGE_TYPE_AVATAR = "avatar"
FILE_USAGE_TYPE_FAVICON = "favicon"
FILE_USAGE_TYPE_APPICON = "appicon"
FILE_USAGE_TYPE_LOGO = "logo"
FILE_USAGE_TYPE_CHAT_GROUP_IMAGE = "chat_group_image"
FILE_USAGE_TYPE_ATTACHMENT_VIDEO = "attachment_video"
FILE_USAGE_TYPE_SCREENSHOT = "screenshot"
FILE_USAGE_TYPE_NAVIGATION_EXTENSION_FILE = "navigation_extension_file"
FILE_USAGE_TYPE_NAVIGATION_EXTENSION_ICON = "navigation_extension_icon"
FILE_USAGE_TYPE_VOICE_RECORDING = "voice_recording"


FILE_UPLOAD_TYPE_NAVIGATION_EXTENSION_FILE = "navigation_extension_file"
FILE_UPLOAD_TYPE_PHOTO = "photo"
FILE_UPLOAD_TYPE_VIDEO = "video"
FILE_UPLOAD_TYPE_FILE = "file"
FILE_UPLOAD_TYPE_IMPORT = "import"
FILE_UPLOAD_TYPE_VOICE = "voice"

mime = magic.Magic(mime=True)


def upload_photo_from_path(sdk, file_path):
    return upload_file_from_path(sdk, file_path, upload_type=FILE_UPLOAD_TYPE_PHOTO)


def upload_photo(sdk, file, mime_type=None, file_name=None):
    return upload_file(sdk, file, mime_type=mime_type, file_name=file_name, upload_type=FILE_UPLOAD_TYPE_PHOTO)


def upload_file_from_path(sdk, file_path, upload_type=FILE_UPLOAD_TYPE_FILE):
    mime_type = mime.from_file(file_path)
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as file:
        return upload_file(sdk, file, upload_type=upload_type, mime_type=mime_type, file_name=file_name)


def upload_file(sdk, file, upload_type=FILE_UPLOAD_TYPE_FILE, mime_type=None, file_name=None):
    token = sdk.get(API_ENDPOINT, upload_type, "upload", "token")
    form_data = {}
    file_content = file.read()

    if not mime_type:
        mime_type = mime.from_buffer(file_content)
    if not file_name:
        file_name = "file"

    for form_param in token.get("additional_form_data", []):
        form_data[form_param["name"]] = form_param["value"]
    form_data[token["file_param_name"]] = file_content

    response = requests.post(token["upload_url"], files=form_data)

    if token.get("registration_required", False):
        if token["upload_response_data_type"] == "xml":
            parsed_response = ElementTree.fromstring(response.content)
            file_key = parsed_response.find("Key").text
        else:
            raise ValueError("Did not receive expected content type for file upload")

        registration_payload = {
            "media_type": mime_type,
            "key": file_key,
            "size": len(file_content),
            "name": file_name,
        }

        response = sdk.post(API_ENDPOINT, upload_type, "upload", payload=registration_payload)
        return FileData(response)
    else:
        if token["upload_response_data_type"] == "json":
            return FileData(response.json())
        else:
            raise ValueError("Did not receive expected content type for file upload")


def get_presigned_url_for(sdk, file_url):
    # TODO validate url
    return sdk.follow_redirect(file_url)


class FileData:
    def __init__(self, raw_data=None):
        self._raw = raw_data or {}

    def get_name(self):
        return self._raw.get("name")

    def get_url(self):
        return self._raw.get("url")

    def get_key(self):
        return self._raw.get("key")

    def get_userid(self):
        return self._raw.get("userid")

    def get_media_type(self):
        return self._raw.get("media_type")

    def get_id(self):
        return self._raw.get("id")

    def get_versions(self):
        return [FileVersion(raw_data=version) for version in self._raw.get("versions", [])]

    def retrieve_presigned_url(self, sdk):
        return get_presigned_url_for(sdk, self.get_url())


class FileVersion:
    def __init__(self, raw_data=None):
        self._raw = raw_data or {}

    def get_name(self):
        return self._raw.get("name")

    def get_url(self):
        return self._raw.get("url")

    def get_width(self):
        return self._raw.get("width")

    def get_height(self):
        return self._raw.get("height")

    def retrieve_presigned_url(self, sdk):
        return get_presigned_url_for(sdk, self.get_url())
