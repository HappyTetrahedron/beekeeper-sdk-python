from typing import Iterator
from typing import List

from beekeeper_sdk.files import FileData

from beekeeper_sdk.iterators import BeekeeperApiLimitAfterIterator
from beekeeper_sdk.iterators import BeekeeperApiLimitBeforeIterator
from beekeeper_sdk.iterators import BeekeeperApiLimitOffsetIterator

API_ENDPOINT = 'conversations'
MESSAGES_ENDPOINT = 'messages'

USER_ROLE_ADMIN = 'admin'
USER_ROLE_MEMBER = 'member'

MESSAGE_TYPE_REGULAR = 'regular'
MESSAGE_TYPE_EVENT = 'event'
MESSAGE_TYPE_CONTROL = 'control'

CONVERSATION_FOLDER_INBOX = 'inbox'
CONVERSATION_FOLDER_ARCHIVE = 'archive'

CONVERSATION_TYPE_ONE_ON_ONE = 'one_on_one'
CONVERSATION_TYPE_GROUP = 'group'

CONVERSATION_MESSAGE_RECEIPT_TYPE_SENT = 'sent'
CONVERSATION_MESSAGE_RECEIPT_TYPE_READ = 'read'


class ConversationApi:
    """Helper class to interact with the Beekeeper Conversation API"""

    def __init__(self, sdk):
        self.sdk = sdk

    def get_conversations(self, folder=None, limit=None, before=None) -> List['Conversation']:
        """Retrieve conversations from `folder`

        Retrieves the most recent `limit` conversations that are older than `before` from the `folder` folder.
        :param folder: Which folder to retrieve conversations from. One of `CONVERSATION_FOLDER_INBOX` or `CONVERSATION_FOLDER_ARCHIVE`
        :param limit: The maximum number of conversations to retrieve. Cannot be larger than 50.
        :param before: Only conversations whose last activity was before this timestamp are returned.
        :return List of Conversation objects
        """
        query = {}
        if folder is not None:
            query['folder'] = folder
        if limit:
            query['limit'] = limit
        if before is not None:
            query['before'] = before
        response = self.sdk.api_client.get(API_ENDPOINT, query=query)
        return [Conversation(self.sdk, raw_data=conversation) for conversation in response]

    def get_conversations_iterator(self, folder=None) -> Iterator['Conversation']:
        """Retrieve conversations from `folder`

        Returns an iterator over conversations from the `folder` folder, from newest (most recently active) to oldest.
        :param folder: Which folder to retrieve conversations from. One of `CONVERSATION_FOLDER_INBOX` or `CONVERSATION_FOLDER_ARCHIVE`
        :return Iterator of Conversation objects
        """
        def call(before=None, limit=None):
            return self.get_conversations(folder=folder, before=before, limit=limit)
        return BeekeeperApiLimitBeforeIterator(call)

    def create_new_conversation(
            self,
            conversation_name,
            user_ids,
            group_image=None,
            conversation_type=CONVERSATION_TYPE_GROUP,
    ) -> 'Conversation':
        """Create a new conversation

        Creates a new conversation with the specified users
        :param conversation_name: Name of the new conversation. Only applicable for group conversations.
        :param user_ids: List of User IDs of users which should be included in the conversation.
        :param group_image: FileData object corresponding to the desired group chat image, default None
        :param conversation_type: What type of conversation to create. One of `CONVERSATION_TYPE_GROUP` (default), `CONVERSATION_TYPE_ONE_ON_ONE`
        :return Conversation object representing the new conversation.
        """
        new_conversation = {'name': conversation_name, 'user_ids': user_ids}

        if conversation_type:
            new_conversation['conversation_type'] = conversation_type
        if group_image:
            new_conversation['group_image'] = group_image

        response = self.sdk.api_client.post(API_ENDPOINT, payload=new_conversation)
        return Conversation(self.sdk, response)

    def get_conversation(self, conversation_id) -> 'Conversation':
        """Retrieve a conversation with a specific ID

        :param conversation_id: ID of the conversation to retrieve
        :return Conversation object representing the conversation.
        """
        response = self.sdk.api_client.get(API_ENDPOINT, conversation_id)
        return Conversation(self.sdk, raw_data=response)

    def get_conversation_by_user(self, user_id) -> 'Conversation':
        """Retrieve a one-on-one conversation with a specific user

        The conversation will be created if it does not yet exist.

        :param user_id: ID of the user whose conversation is to retrieve
        :return Conversation object representing the conversation.
        """
        response = self.sdk.api_client.get(API_ENDPOINT, 'by_user', user_id)
        return Conversation(self.sdk, raw_data=response)

    def send_message_to_conversation(self, conversation_id, message) -> 'ConversationMessage':
        """Send a message to the conversation with specified `conversation_id`

        :param conversation_id: ID of the conversation in which to send the message
        :param message: ConversationMessage object representing the message, or string
        :return ConversationMessage object representing the sent message.
        """
        real_message = self._messageify(message)
        response = self.sdk.api_client.post(
            API_ENDPOINT,
            conversation_id,
            MESSAGES_ENDPOINT,
            payload=real_message._raw,
        )
        return ConversationMessage(self.sdk, raw_data=response)

    def leave_conversation(self, conversation_id):
        """Leave the conversation with specified `conversation_id`

        :param conversation_id: ID of the conversation to leave
        """
        response = self.sdk.api_client.post(API_ENDPOINT, conversation_id, 'leave')
        return response.get('status') == 'OK'

    def archive_conversation(self, conversation_id) -> 'Conversation':
        """Archive the conversation with specified `conversation_id`

        :param conversation_id: ID of the conversation to archive
        :return Conversation object representing the archived conversation
        """
        response = self.sdk.api_client.post(API_ENDPOINT, conversation_id, 'archive')
        return Conversation(self.sdk, raw_data=response)

    def un_archive_conversation(self, conversation_id) -> 'Conversation':
        """Un-Archive the conversation with specified `conversation_id` (move to inbox)

        :param conversation_id: ID of the conversation to un-archive
        :return Conversation object representing the un-archived conversation
        """
        response = self.sdk.api_client.delete(API_ENDPOINT, conversation_id, 'archive')
        return Conversation(self.sdk, raw_data=response)

    def add_user_to_conversation(self, conversation_id, user_id, role=USER_ROLE_MEMBER) -> 'ConversationMember':
        """Add user with ID `user_id` to conversation with ID `conversation_id`

        :param conversation_id: ID of the conversation to which to add the user
        :param user_id: ID of the user which is to be added to the conversation
        :param role: Role the new user should have in the conversation. One of `USER_ROLE_MEMBER` (default), `USER_ROLE_ADMIN`
        :return ConversationMember object representing the newly added conversation member
        """
        body = {'role': role}
        response = self.sdk.api_client.put(API_ENDPOINT, conversation_id, 'members', user_id, payload=body)
        return ConversationMember(self.sdk, raw_data=response)

    def remove_user_from_conversation(self, conversation_id, user_id):
        """Remove user with ID `user_id` from conversation with ID `conversation_id`

        :param conversation_id: ID of the conversation from which to remove the user
        :param user_id: ID of the user which is to be removed from the conversation
        """
        response = self.sdk.api_client.delete(API_ENDPOINT, conversation_id, 'members', user_id)
        return response.get('status') == 'OK'

    def get_members_of_conversation_iterator(
            self,
            conversation_id,
            include_suspended=False
    ) -> Iterator['ConversationMember']:
        """Retrieve members of conversation with ID `conversation_id`

        Returns an iterator over members in the conversation with ID `conversation_id` (in alphabetical order)
        :param conversation_id: ID of the conversation for which to get members
        :param include_suspended: Boolean indicating whether to include suspended users in the result
        :return Iterator of ConversationMember objects
        """
        def call(offset=None, limit=None):
            return self.get_members_of_conversation(
                conversation_id,
                include_suspended=include_suspended,
                offset=offset,
                limit=limit
            )
        return BeekeeperApiLimitOffsetIterator(call)

    def get_members_of_conversation(
            self,
            conversation_id,
            include_suspended=None,
            limit=None,
            offset=None
    ) -> List['ConversationMember']:
        """Retrieve members of conversation with ID `conversation_id`

        Retrieves the first `limit` members (alphabetically) of the conversation `conversation_id` after an offset `offset`
        :param conversation_id: ID of the conversation for which to get members
        :param include_suspended: Boolean indicating whether to include suspended users in the result
        :param limit: How many users to retrieve. Cannot be more than 50.
        :param offset: The list offset from which to retrieve users.
        :return List of ConversationMember objects
        """
        query = {}
        if include_suspended is not None:
            query['include_suspended'] = include_suspended
        if limit:
            query['limit'] = limit
        if offset is not None:
            query['offset'] = offset
        response = self.sdk.api_client.get(API_ENDPOINT, conversation_id, 'members', query=query)
        return [ConversationMember(self.sdk, raw_data=member) for member in response]

    def get_messages_of_conversation_iterator(
            self,
            conversation_id,
            reversed_order=False
        ) -> Iterator['ConversationMessage']:
        """Retrieve messages of conversation with ID `conversation_id`

        :param conversation_id: ID of the conversation for which to get members
        :param reversed_order: Boolean indicating whether the order of messages should be reversed
        (oldest-to-newest instead of newest-to-oldest)

        :return Iterator of ConversationMessage objects
        """
        if reversed_order:
            def call(after=None, limit=None):
                return self.get_messages_of_conversation(conversation_id, after=after, limit=limit)
            return BeekeeperApiLimitAfterIterator(call, response_is_reversed=True)

        def call(before=None, limit=None):
            return self.get_messages_of_conversation(conversation_id, before=before, limit=limit)
        return BeekeeperApiLimitBeforeIterator(call, response_is_reversed=True)

    def get_messages_of_conversation(
            self,
            conversation_id,
            after=None,
            before=None,
            limit=None,
            message_id=None
    ) -> List['ConversationMessage']:
        """Retrieve messages of conversation with ID `conversation_id`

        Retrieves the most recent `limit` messages of the conversation `conversation_id`
        that were sent before timestamp `before` (defaults to current time), or the oldest
        `limit` messages that were sent after timestamp `after`.

        Specifying both `before` and `after` results in undefined behaviour.

        :param conversation_id: ID of the conversation for which to get members
        :param after: Only messages sent after this timestamp are returned.
        :param before: Only messages sent before this timestamp are returned.
        :param limit: How many messages to retrieve. Cannot be more than 50.
        :param message_id: Can be specified instead of `before` or `after` to retrieve `limit` messages around
        `message_id`, i.e. returns [limit messages before message_id] + [message_id] + [limit messages after message_id]
        :return List of ConversationMessage objects
        """
        query = {}
        if message_id is not None:
            query['message_id'] = message_id
        if limit:
            query['limit'] = limit
        if after is not None:
            query['after'] = after
        if before is not None:
            query['before'] = before
        response = self.sdk.api_client.get(API_ENDPOINT, conversation_id, MESSAGES_ENDPOINT, query=query)
        return [ConversationMessage(self.sdk, raw_data=message) for message in response]

    def _messageify(self, message_or_string):
        if isinstance(message_or_string, str):
            return ConversationMessage(self.sdk, text=message_or_string)
        return message_or_string


class ConversationMessage:
    """Representation of a message in a Conversation"""
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
        """
        :param sdk: BeekeeperSDK
        :param raw_data: Raw API representation. Not required.
        :param text: Text of the message
        :param message_type: Type of the message. One of MESSAGE_TYPE_REGULAR, MESSAGE_TYPE_EVENT, MESSAGE_TYPE_CONTROL
        :param files: List of FileData objects representing files attached to this message
        :param media: List of FileData objects representing media attached to this message
        :param addons: List of addons attached to this message
        """
        self.sdk = sdk
        self._raw = raw_data or {}
        if text:
            self._raw['text'] = text
        if message_type:
            self._raw['message_type'] = message_type

        if files:
            self._raw['files'] = [file._raw for file in files]
        if media:
            self._raw['media'] = [medium._raw for medium in media]

        if addons:
            self._raw['addons'] = [addon._raw for addon in addons]

    def _timestamp(self):
        return self.get_created()

    def get_conversation_id(self) -> int:
        """Returns the ID of the conversation this message was sent in"""
        return self._raw.get('conversation_id')

    def get_id(self) -> str:
        """Returns the ID of this message"""
        return self._raw.get('id')

    def get_text(self) -> str:
        """Returns the text of this message"""
        return self._raw.get('text')

    def get_type(self):
        """Returns the type of this message.
        One of `MESSAGE_TYPE_REGULAR`, `MESSAGE_TYPE_EVENT`, `MESSAGE_TYPE_CONTROL`
        """
        return self._raw.get('message_type')

    def get_profile(self) -> str:
        """Returns the username of the sender of this message"""
        return self._raw.get('profile')

    def get_user_id(self) -> str:
        """Returns the user ID of the sender of this message"""
        return self._raw.get('user_id')

    def get_name(self) -> str:
        """Returns the name of the sender of this message"""
        return self._raw.get('name')

    def get_created(self) -> str:
        """Returns the timestamp of this message's creation"""
        return self._raw.get('created')

    def get_files(self) -> List['FileData']:
        """Returns a list of FileData objects attached to this message as files"""
        return [FileData(self.sdk, raw_data=file) for file in self._raw.get('files', [])]

    def get_media(self) -> List['FileData']:
        """Returns a list of FileData objects attached to this message as media"""
        return [FileData(self.sdk, raw_data=file) for file in self._raw.get('media', [])]

    def get_addons(self) -> List['ConversationMessageAddon']:
        """Returns a list of ConversationMessageAddon objects attached to this message"""
        return [ConversationMessageAddon(self.sdk, raw_data=addon) for addon in self._raw.get('addons', [])]

    def reply(self, message) -> 'ConversationMessage':
        """Send a message to the same conversation this message comes from
        :param message: ConversationMessage object representing the message to be sent, or string
        """
        self.sdk.conversations.send_message_to_conversation(self.get_conversation_id(), message)


class Conversation:
    """Representation of a conversation"""
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def _timestamp(self):
        return self.get_modified()

    def get_type(self):
        """Returns the conversation type. One of `CONVERSATION_TYPE_GROUP`, `CONVERSATION_TYPE_ONE_ON_ONE`"""
        return self._raw.get('conversation_type')

    def get_id(self) -> int:
        """Returns the ID of this conversation"""
        return self._raw.get('id')

    def get_name(self) -> str:
        """Returns the name this conversation"""
        return self._raw.get('name')

    def get_snippet(self) -> str:
        """Returns the snippet (short excerpt of most recent message) of this conversation"""
        return self._raw.get('snippet')

    def get_profile(self) -> str:
        return self._raw.get('profile')

    def get_modified(self) -> str:
        """Returns the timestamp at which this conversation was last modified"""
        return self._raw.get('modified')

    def get_is_admin(self) -> bool:
        """Returns true if the BeekeeperSDK has admin rights in this conversation"""
        return self._raw.get('is_admin')

    def get_avatar(self) -> str:
        return self._raw.get('avatar')

    def get_user_id(self) -> str:
        """Returns the ID of the user this conversation is with (only for `CONVERSATION_TYPE_ONE_ON_ONE`)"""
        return self._raw.get('user_id')

    def get_folder(self):
        """Returns the folder this conversation resides in.
        One of `CONVERSATION_FOLDER_INBOX` or `CONVERSATION_FOLDER_ARCHIVE`
        """
        return self._raw.get('folder')

    def send_message(self, message) -> 'Conversation':
        """Sends a message to this conversation
        :param message: ConversationMessage object representing the message to be sent, or string
        """
        return self.sdk.conversations.send_message_to_conversation(self.get_id(), message)

    def change_name(self, new_name) -> 'Conversation':
        """Change the name of this conversation

        Requires admin rights within this conversation
        :param new_name: String containing the new name of the conversation
        """
        self._raw['name'] = new_name
        return self._save()

    def change_avatar(self, new_avatar) -> 'Conversation':
        self._raw['avatar'] = new_avatar
        return self._save()

    def leave(self):
        """Leave this conversation"""
        return self.sdk.conversations.leave_conversation(self.get_id())

    def archive(self) -> 'Conversation':
        """Move this conversation to the "Archive" folder"""
        return self.sdk.conversations.archive_conversation(self.get_id())

    def un_archive(self) -> 'Conversation':
        """Move this conversation to the "Inbox" folder"""
        return self.sdk.conversations.un_archive_conversation(self.get_id())

    def add_user(self, user_id, role=USER_ROLE_MEMBER) -> 'ConversationMember':
        """Add user with ID `user_id` to this conversation

        :param user_id: ID of the user which is to be added to the conversation
        :param role: Role the new user should have in the conversation. One of `USER_ROLE_MEMBER` (default), `USER_ROLE_ADMIN`
        :return ConversationMember object representing the newly added conversation member
        """
        return self.sdk.conversations.add_user_to_conversation(self.get_id(), user_id, role=role)

    def remove_user(self, user_id):
        """Remove user with ID `user_id` from this conversation

        :param user_id: ID of the user which is to be removed from the conversation
        """
        return self.sdk.conversations.remove_user_from_conversation(self.get_id(), user_id)

    def retrieve_members(self, include_suspended=None, limit=None, offset=None) -> List['ConversationMember']:
        """Retrieve members of this conversation from the API

        Retrieves the first `limit` members (alphabetically) of this conversation after an offset `offset`
        :param include_suspended: Boolean indicating whether to include suspended users in the result
        :param limit: How many users to retrieve. Cannot be more than 50.
        :param offset: The list offset from which to retrieve users.
        :return List of ConversationMember objects
        """
        return self.sdk.conversations.get_members_of_conversation(self.get_id(), include_suspended, limit, offset)

    def retrieve_messages(self, after=None, before=None, limit=None, message_id=None) -> List['ConversationMessage']:
        """Retrieve messages of this conversation from the API

        Retrieves the most recent `limit` messages of this conversation
        that were sent before timestamp `before` (defaults to current time), or the oldest
        `limit` messages that were sent after timestamp `after`.

        Specifying both `before` and `after` results in undefined behaviour.

        :param after: Only messages sent after this timestamp are returned.
        :param before: Only messages sent before this timestamp are returned.
        :param limit: How many messages to retrieve. Cannot be more than 50.
        :param message_id: Can be specified instead of `before` or `after` to retrieve `limit` messages around
        `message_id`, i.e. returns [limit messages before message_id] + [message_id] + [limit messages after message_id]
        :return List of ConversationMessage objects
        """
        return self.sdk.conversations.get_messages_of_conversation(self.get_id(), after, before, limit, message_id)

    def retrieve_members_iterator(self, include_suspended=None) -> Iterator['ConversationMember']:
        """Retrieve members of this conversation from the API

        Returns an iterator over members in this conversation  (in alphabetical order)
        :param include_suspended: Boolean indicating whether to include suspended users in the result
        :return Iterator of ConversationMember objects
        """
        return self.sdk.conversations.get_members_of_conversation_iterator(self.get_id(), include_suspended)

    def retrieve_messages_iterator(self, reversed_order=False) -> Iterator['ConversationMessage']:
        """Retrieve messages of this conversation from the API

        :param reversed_order: Boolean indicating whether the order of messages should be reversed
        (oldest-to-newest instead of newest-to-oldest)

        :return Iterator of ConversationMessage objects
        """
        return self.sdk.conversations.get_messages_of_conversation_iterator(
            self.get_id(),
            reversed_order=reversed_order
        )

    def _save(self) -> 'Conversation':
        response = self.sdk.api_client.put(
            API_ENDPOINT,
            self.get_id(),
            payload=self._raw,
        )
        self._raw = response
        return self


class ConversationMember:
    """Representation of a member inside a conversation"""
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_role(self):
        """Returns the role of this member in this conversation. One of `USER_ROLE_MEMBER`, `USER_ROLE_ADMIN`"""
        return self._raw.get('role')

    def get_name(self) -> str:
        """Returns the name of this conversation member"""
        return self._raw.get('user', {}).get('name')

    def get_display_name(self) -> str:
        """Returns the display name of this conversation member"""
        return self._raw.get('user', {}).get('display_name')

    def get_id(self) -> str:
        """Returns the ID of the user represented by this ConversationMember"""
        return self._raw.get('user', {}).get('id')

    def get_suspended(self) -> bool:
        """Returns true if this conversation member is suspended"""
        return self._raw.get('user', {}).get('suspended')

    def get_avatar(self) -> str:
        """Returns the avatar of this conversation member"""
        return self._raw.get('user', {}).get('avatar')


class ConversationMessageInfo:
    """Representation of conversation message information,
    which contains information on who has read a specific message
    """
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_message(self) -> 'ConversationMessage':
        """Returns the message this information pertains to"""
        return ConversationMessage(self.sdk, raw_data=self._raw.get('message'))

    def get_message_receipts(self) -> List['ConversationMessageReceipt']:
        """Returns the message receipts for this message"""
        return [ConversationMessageReceipt(self.sdk, raw_data=receipt)
                for receipt in self._raw.get('message_receipts', [])]


class ConversationMessageReceipt:
    """Representation of a message receipt, which contains information on whether a specific user has received or read
    a specific message
    """
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_id(self) -> str:
        return self._raw.get('id')

    def get_user_id(self) -> str:
        """Returns the ID of the user this receipt pertains to"""
        return self._raw.get('user_id')

    def get_message_id(self) -> str:
        """Returns the ID of the message this receipt pertains to"""
        return self._raw.get('message_id')

    def get_type(self):
        """Returns the type of this receipt, one of
        `CONVERSATION_MESSAGE_RECEIPT_TYPE_SENT`, `CONVERSATION_MESSAGE_RECEIPT_TYPE_READ`

        `CONVERSATION_MESSAGE_RECEIPT_TYPE_SENT` indicates the message has been sent, but not read by the user yet
        `CONVERSATION_MESSAGE_RECEIPT_TYPE_READ` indicates the message has been read by the user.
        """
        return self._raw.get('receipt_type')

    def get_created(self):
        return self._raw.get('created')

    def get_user_name(self) -> str:
        """Returns the name of the user"""
        return self._raw.get('user', {}).get('name')

    def get_user_display_name(self) -> str:
        """Returns the display name of the user"""
        return self._raw.get('user', {}).get('display_name')

    def get_user_avatar(self) -> str:
        return self._raw.get('user', {}).get('avatar')


class ConversationMessageAddon:
    """Represents a message addon, which can contain various metadata"""
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_type(self):
        """Returns the type of the addon"""
        return self._raw.get('addon_type')

    def get_id(self) -> str:
        return self._raw.get('uuid')

    # TODO add representations for concrete addon types
