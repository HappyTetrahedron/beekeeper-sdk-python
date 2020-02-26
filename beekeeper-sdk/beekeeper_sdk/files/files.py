import requests
from xml.etree import ElementTree
import magic
import mimetypes
import os


API_ENDPOINT = 'files'

FILE_USAGE_TYPE_ATTACHMENT_IMAGE = 'attachment_image'
FILE_USAGE_TYPE_ATTACHMENT_FILE = 'attachment_file'
FILE_USAGE_TYPE_COVER_IMAGE = 'cover_image'
FILE_USAGE_TYPE_AVATAR = 'avatar'
FILE_USAGE_TYPE_FAVICON = 'favicon'
FILE_USAGE_TYPE_APPICON = 'appicon'
FILE_USAGE_TYPE_LOGO = 'logo'
FILE_USAGE_TYPE_CHAT_GROUP_IMAGE = 'chat_group_image'
FILE_USAGE_TYPE_ATTACHMENT_VIDEO = 'attachment_video'
FILE_USAGE_TYPE_SCREENSHOT = 'screenshot'
FILE_USAGE_TYPE_NAVIGATION_EXTENSION_FILE = 'navigation_extension_file'
FILE_USAGE_TYPE_NAVIGATION_EXTENSION_ICON = 'navigation_extension_icon'
FILE_USAGE_TYPE_VOICE_RECORDING = 'voice_recording'


FILE_UPLOAD_TYPE_NAVIGATION_EXTENSION_FILE = 'navigation_extension_file'
FILE_UPLOAD_TYPE_PHOTO = 'photo'
FILE_UPLOAD_TYPE_VIDEO = 'video'
FILE_UPLOAD_TYPE_FILE = 'file'
FILE_UPLOAD_TYPE_IMPORT = 'import'
FILE_UPLOAD_TYPE_VOICE = 'voice'

mime = magic.Magic(mime=True)


class FileApi:

    def __init__(self, sdk):
        self.sdk = sdk

    def upload_photo_from_path(self, file_path):
        return self.sdk.files.upload_file_from_path(file_path, upload_type=FILE_UPLOAD_TYPE_PHOTO)

    def upload_photo(self, file, mime_type=None, file_name=None):
        return self.upload_file(file, mime_type=mime_type, file_name=file_name, upload_type=FILE_UPLOAD_TYPE_PHOTO)

    def upload_file_from_path(self, file_path, upload_type=FILE_UPLOAD_TYPE_FILE):
        mime_type = mime.from_file(file_path)
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as file:
            return self.upload_file(file, upload_type=upload_type, mime_type=mime_type, file_name=file_name)

    def upload_file(self, file, upload_type=FILE_UPLOAD_TYPE_FILE, mime_type=None, file_name=None):
        token = self.sdk.api_client.get(API_ENDPOINT, upload_type, 'upload', 'token')
        form_data = {}
        file_content = file.read()

        if not mime_type:
            mime_type = mime.from_buffer(file_content)
        if not file_name:
            ext = mimetypes.guess_extension(mime_type)
            if ext:
                file_name = 'upload{}'.format(ext)
            else:
                file_name = 'upload'

        for form_param in token.get('additional_form_data', []):
            form_data[form_param['name']] = form_param['value']
        form_data[token['file_param_name']] = file_content

        response = requests.post(token['upload_url'], files=form_data)

        if token.get('registration_required', False):
            if token['upload_response_data_type'] == 'xml':
                parsed_response = ElementTree.fromstring(response.content)
                file_key = parsed_response.find('Key').text
            else:
                raise ValueError("Did not receive expected content type for file upload")

            registration_payload = {
                'media_type': mime_type,
                'key': file_key,
                'size': len(file_content),
                'name': file_name,
            }

            response = self.sdk.api_client.post(API_ENDPOINT, upload_type, 'upload', payload=registration_payload)
            return FileData(self.sdk, raw_data=response)
        else:
            if token['upload_response_data_type'] == 'json':
                return FileData(self.sdk, raw_data=response.json())
            else:
                raise ValueError("Did not receive expected content type for file upload")

    def get_presigned_url_for(self, file_url):
        # TODO validate url
        return self.sdk.api_client.get_redirect_url(file_url)


class FileData:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_name(self):
        return self._raw.get('name')

    def get_url(self):
        return self._raw.get('url')

    def get_key(self):
        return self._raw.get('key')

    def get_userid(self):
        return self._raw.get('userid')

    def get_media_type(self):
        return self._raw.get('media_type')

    def get_id(self):
        return self._raw.get('id')

    def get_versions(self):
        return [FileVersion(self.sdk, raw_data=version) for version in self._raw.get('versions', [])]

    def retrieve_presigned_url(self):
        return self.sdk.files.get_presigned_url_for(self.get_url())


class FileVersion:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_name(self):
        return self._raw.get('name')

    def get_url(self):
        return self._raw.get('url')

    def get_width(self):
        return self._raw.get('width')

    def get_height(self):
        return self._raw.get('height')

    def retrieve_presigned_url(self, sdk):
        return self.sdk.files.get_presigned_url_for(sdk, self.get_url())
