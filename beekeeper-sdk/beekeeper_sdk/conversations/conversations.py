from beekeeper_sdk.files import FileData

API_ENDPOINT = "conversations"
MESSAGES_ENDPOINT = "messages"

USER_ROLE_ADMIN = "admin"
USER_ROLE_MEMBER = "member"

MESSAGE_TYPE_REGULAR = "regular"
MESSAGE_TYPE_EVENT = "event"
MESSAGE_TYPE_CONTROL = "control"

CONVERSATION_FOLDER_INBOX = "inbox"
CONVERSATION_FOLDER_ARCHIVE = "archive"

CONVERSATION_TYPE_ONE_ON_ONE = "one_on_one"
CONVERSATION_TYPE_GROUP = "group"


class ConversationApi:

    def __init__(self, sdk):
        self.sdk = sdk

    def get_conversations(self, folder=None, limit=None, before=None):
        query = {}
        if folder is not None:
            query["folder"] = folder
        if limit:
            query["limit"] = limit
        if before is not None:
            query["before"] = before
        response = self.sdk.get(API_ENDPOINT, query=query)
        return [Conversation(self.sdk, raw_data=conversation) for conversation in response]

    def create_new_conversation(self, conversation_name, user_ids, group_image=None,
                                conversation_type=CONVERSATION_TYPE_GROUP):
        new_conversation = {"name": conversation_name, "user_ids": user_ids}

        if conversation_type:
            new_conversation["conversation_type"] = conversation_type
        if group_image:
            new_conversation["group_image"] = group_image

        response = self.sdk.post(API_ENDPOINT, payload=new_conversation)
        return Conversation(self.sdk, response)

    def get_conversation(self, conversation_id):
        response = self.sdk.get(API_ENDPOINT, conversation_id)
        return Conversation(self.sdk, raw_data=response)

    def get_conversation_by_user(self, user_id):
        response = self.sdk.get(API_ENDPOINT, "by_user", user_id)
        return Conversation(self.sdk, raw_data=response)

    def send_message_to_conversation(self, conversation_id, message):
        real_message = self._messageify(message)
        response = self.sdk.post(API_ENDPOINT, conversation_id, MESSAGES_ENDPOINT,
                                 payload=real_message._raw)
        return ConversationMessage(self.sdk, raw_data=response)

    def leave_conversation(self, conversation_id):
        response = self.sdk.post(API_ENDPOINT, conversation_id, "leave")
        return response.get("status") == "OK"

    def archive_conversation(self, conversation_id):
        response = self.sdk.post(API_ENDPOINT, conversation_id, "archive")
        return Conversation(self.sdk, raw_data=response)

    def un_archive_conversation(self, conversation_id):
        response = self.sdk.delete(API_ENDPOINT, conversation_id, "archive")
        return Conversation(self.sdk, raw_data=response)

    def add_user_to_conversation(self, conversation_id, user_id, role=USER_ROLE_MEMBER):
        body = {"role": role}
        response = self.sdk.put(API_ENDPOINT, conversation_id, "members", user_id,
                                payload=body)
        return ConversationMember(self.sdk, raw_data=response)

    def remove_user_from_conversation(self, conversation_id, user_id):
        response = self.sdk.delete(API_ENDPOINT, conversation_id, "members", user_id)
        return response.get("status") == "OK"

    def get_members_of_conversation(self, conversation_id, include_suspended=None, limit=None, offset=None):
        query = {}
        if include_suspended is not None:
            query["include_suspended"] = include_suspended
        if limit:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        response = self.sdk.get(API_ENDPOINT, conversation_id, "members", query=query)
        return [ConversationMember(self.sdk, raw_data=member) for member in response]

    def get_messages_of_conversation(self, conversation_id, after=None, before=None, limit=None, message_id=None):
        query = {}
        if message_id is not None:
            query["message_id"] = message_id
        if limit:
            query["limit"] = limit
        if after is not None:
            query["after"] = after
        if before is not None:
            query["before"] = before
        response = self.sdk.get(API_ENDPOINT, conversation_id, MESSAGES_ENDPOINT, query=query)
        return [ConversationMessage(self.sdk, raw_data=message) for message in response]

    def _messageify(self, message_or_string):
        if isinstance(message_or_string, str):
            return ConversationMessage(self.sdk, text=message_or_string)
        return message_or_string


class ConversationMessage:
    def __init__(
            self,
            sdk,
            raw_data=None,
            text=None,
            message_type=None,
            files=None,
            media=None,
            addons=None,

    ):
        self.sdk = sdk
        self._raw = raw_data or {}
        if text:
            self._raw["text"] = text
        if message_type:
            self._raw["message_type"] = message_type

        if files:
            self._raw["files"] = [file._raw for file in files]
        if media:
            self._raw["media"] = [medium._raw for medium in media]

        if addons:
            self._raw["addons"] = [addon._raw for addon in addons]

    def get_conversation_id(self):
        return self._raw.get("conversation_id")

    def get_id(self):
        return self._raw.get("id")

    def get_text(self):
        return self._raw.get("text")

    def get_type(self):
        return self._raw.get("message_type")

    def get_profile(self):
        return self._raw.get("profile")

    def get_user_id(self):
        return self._raw.get("user_id")

    def get_name(self):
        return self._raw.get("name")

    def get_created(self):
        return self._raw.get("created")

    def get_files(self):
        return [FileData(self.sdk, raw_data=file) for file in self._raw.get("files", [])]

    def get_media(self):
        return [FileData(self.sdk, raw_data=file) for file in self._raw.get("media", [])]

    def get_addons(self):
        return [ConversationMessageAddon(self.sdk, raw_data=addon) for addon in self._raw.get("addons", [])]

    def reply(self, message):
        self.sdk.conversations.send_message_to_conversation(self.get_conversation_id(), message)


class Conversation:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_type(self):
        return self._raw.get("conversation_type")

    def get_id(self):
        return self._raw.get("id")

    def get_name(self):
        return self._raw.get("name")

    def get_snippet(self):
        return self._raw.get("snippet")

    def get_profile(self):
        return self._raw.get("profile")

    def get_modified(self):
        return self._raw.get("modified")

    def get_is_admin(self):
        return self._raw.get("is_admin")

    def get_avatar(self):
        return self._raw.get("avatar")

    def get_user_id(self):
        return self._raw.get("user_id")

    def get_folder(self):
        return self._raw.get("folder")

    def send_message(self, message):
        return self.sdk.conversations.send_message_to_conversation(self.get_id(), message)

    def change_name(self, new_name):
        self._raw["name"] = new_name
        return self._save()

    def change_avatar(self, new_avatar):
        self._raw["avatar"] = new_avatar
        return self._save()

    def leave(self):
        return self.sdk.conversations.leave_conversation(self.get_id())

    def archive(self):
        return self.sdk.conversations.archive_conversation(self.get_id())

    def un_archive(self):
        return self.sdk.conversations.un_archive_conversation(self.get_id())

    def add_user(self, user_id, role=USER_ROLE_MEMBER):
        return self.sdk.conversations.add_user_to_conversation(self.get_id(), user_id, role=role)

    def remove_user(self, user_id):
        return self.sdk.conversations.remove_user_from_conversation(self.get_id(), user_id)

    def retrieve_members(self, include_suspended=None, limit=None, offset=None):
        return self.sdk.conversations.get_members_of_conversation(self.get_id(), include_suspended, limit, offset)

    def retrieve_messages(self, after=None, before=None, limit=None, message_id=None):
        return self.sdk.conversations.get_messages_of_conversation(self.get_id(), after, before, limit, message_id)

    def _save(self):
        response = self.sdk.put(API_ENDPOINT, self.get_id(),
                           payload=self._raw)
        self._raw = response
        return self


class ConversationMember:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_role(self):
        return self._raw.get("role")

    def get_user(self):
        # TODO turn into user object
        return self._raw.get("user")


class ConversationMessageInfo:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_message(self):
        return ConversationMessage(self.sdk, raw_data=self._raw.get("message"))

    def get_message_receipts(self):
        return [ConversationMessageReceipt(self.sdk, raw_data=receipt)
                for receipt in self._raw.get("message_receipts", [])]


class ConversationMessageReceipt:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_id(self):
        return self._raw.get("id")

    def get_user_id(self):
        return self._raw.get("user_id")

    def get_message_id(self):
        return self._raw.get("message_id")

    def get_type(self):
        return self._raw.get("receipt_type")

    def get_created(self):
        return self._raw.get("created")

    def get_user(self):
        # TODO turn into user object
        return self._raw.get("user")


class ConversationMessageAddon:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_type(self):
        return self._raw.get("addon_type")

    def get_id(self):
        return self._raw.get("uuid")

    # TODO add representations for concrete addon types
