from typing import Iterator
from typing import List

from beekeeper_sdk.files import FileData
from beekeeper_sdk.iterators import BeekeeperApiLimitBeforeIterator

STREAM_API_ENDPOINT = 'streams'
POST_API_ENDPOINT = 'posts'
COMMENTS_API_ENDPOINT = 'comments'

COMMENTS_ENDPOINT = 'comments'
POSTS_ENDPOINT = 'posts'
SIMPLE_LIKE_ENDPOINT = 'like'
LIKES_ENDPOINT = 'likes'


class StreamApi:
    """Helper class to interact with the Beekeeper Stream API"""

    def __init__(self, sdk):
        self.sdk = sdk

    def get_streams(self) -> List['Stream']:
        """Retrieve list of streams

        returns a list of Stream objects
        """
        response = self.sdk.api_client.get(STREAM_API_ENDPOINT)
        return [Stream(self.sdk, raw_data=stream) for stream in response]

    def get_stream(self, stream_id) -> 'Stream':
        """Retrieve the stream with a given `stream_id`
        :param stream_id: ID of the stream
        :return Stream object representing the stream
        """
        response = self.sdk.api_client.get(STREAM_API_ENDPOINT, stream_id)
        return Stream(self.sdk, raw_data=response)

    def get_posts_from_stream(self, stream_id, limit=None, include_comments=False, before=None) -> List['Post']:
        """Retrieve posts from a stream

        Retrieves the most recent `limit` posts that are older than `before`
        from the stream with ID `stream_id`

        :param stream_id: ID of the stream from which to retrieve posts
        :param limit: Maximum number of posts to retrieve
        :param include_comments: Whether to include comments in the returned Post objects. Default False.
        :param before: Only posts created before this timestamp are returned.
        :return List of Post objects

        """
        query = {}
        if limit:
            query['limit'] = limit
        if before is not None:
            query['before'] = before
        query['include_comments'] = include_comments
        response = self.sdk.api_client.get(STREAM_API_ENDPOINT, stream_id, POSTS_ENDPOINT, query=query)
        return [Post(self.sdk, raw_data=post) for post in response]

    def get_posts_from_stream_iterator(self, stream_id, include_comments=False) -> Iterator['Post']:
        """Retrieve posts from a stream

        Returns an iterator over posts in a stream, from newest to oldest.

        :param stream_id: ID of the stream from which to retrieve posts
        :param include_comments: Whether to include comments in the returned Post objects. Default False.
        :return Iterator of Post objects

        """
        def call(before=None, limit=None):
            return self.get_posts_from_stream(
                stream_id,
                include_comments=include_comments,
                before=before,
                limit=limit
            )
        return BeekeeperApiLimitBeforeIterator(call)

    def get_post(self, post_id) -> 'Post':
        """Retrieve the post with ID `post_id`

        :param post_id: ID of the post to retrieve
        :return Post object representing the post
        """
        response = self.sdk.api_client.get(POST_API_ENDPOINT, post_id)
        return Post(self.sdk, raw_data=response)

    def delete_post(self, post_id):
        """Delete the post with ID `post_id`

        :param post_id: ID of the post to delete
        """
        response = self.sdk.api_client.delete(POST_API_ENDPOINT, post_id)
        return response.get('status') == 'OK'

    def create_post(self, stream_id, post) -> 'Post':
        """Create a new post in stream with ID `stream_id`

        :param stream_id: ID of the stream in which to create a new post
        :param post: Post object representing the post to be created, or string containing post body.
        :return Post object representing the newly created post
        """
        real_post = self._postify(post)
        response = self.sdk.api_client.post(STREAM_API_ENDPOINT, stream_id, POSTS_ENDPOINT, payload=real_post._raw)
        return Post(self.sdk, raw_data=response)

    def get_post_comments(self, post_id, limit=None, before=None) -> List['PostComment']:
        """Retrieve the newest `limit` comments older than `before` of the post with ID `post_id`

        :param post_id: ID of the post whose comments to retrieve
        :param limit: Maximum number of comments to retreive
        :param before: Only comments older than this timestamp are returned
        :return List of PostComment objects
        """
        query = {}
        if limit:
            query['limit'] = limit
        if before is not None:
            query['before'] = before
        response = self.sdk.api_client.get(POST_API_ENDPOINT, post_id, COMMENTS_ENDPOINT, query=query)
        return [PostComment(self.sdk, raw_data=comment) for comment in response]

    def get_post_comments_iterator(self, post_id) -> Iterator['PostComment']:
        """Retrieve iterator over comments of the post with ID `post_id`

        :param post_id: ID of the post whose comments to retrieve
        :return Iterator of PostComment objects, from newest to oldest
        """
        def call(before=None, limit=None):
            return self.get_post_comments(post_id, before=before, limit=limit)
        return BeekeeperApiLimitBeforeIterator(call)

    def comment_on_post(self, post_id, comment) -> 'PostComment':
        """Create a comment on post with ID `post_id`
        :param post_id: ID of post to comment on
        :param comment: PostComment representing the comment to create, or string
        :return PostComment object representing the newly created comment
        """
        real_comment = self._commentify(comment)
        response = self.sdk.api_client.post(POST_API_ENDPOINT, post_id, COMMENTS_ENDPOINT, payload=real_comment._raw)
        return PostComment(self.sdk, raw_data=response)

    def delete_comment(self, comment_id):
        """Delete the comment with ID `comment_id`

        :param comment_id: ID of the comment to delete
        """
        response = self.sdk.api_client.delete(COMMENTS_API_ENDPOINT, comment_id)
        return response.get('status') == 'OK'

    def like_post(self, post_id) -> 'Post':
        """Like the post with ID `post_id`

        :param post_id: ID of the post to like
        :return Post object representing the liked post
        """
        response = self.sdk.api_client.post(POST_API_ENDPOINT, post_id, SIMPLE_LIKE_ENDPOINT)
        return Post(self.sdk, raw_data=response)

    def unlike_post(self, post_id) -> 'Post':
        """Unlike the post with ID `post_id`

        :param post_id: ID of the post to unlike
        :return Post object representing the unliked post
        """
        response = self.sdk.api_client.delete(POST_API_ENDPOINT, post_id, SIMPLE_LIKE_ENDPOINT)
        return Post(self.sdk, raw_data=response)

    def like_comment(self, comment_id) -> 'PostComment':
        """Like the comment with ID `comment_id`

        :param comment_id: ID of the comment to like
        :return PostComment object representing the liked comment
        """
        response = self.sdk.api_client.post(COMMENTS_API_ENDPOINT, comment_id, SIMPLE_LIKE_ENDPOINT)
        return PostComment(self.sdk, raw_data=response)

    def unlike_comment(self, comment_id) -> 'PostComment':
        """Unlike the comment with ID `comment_id`

        :param comment_id: ID of the comment to unlike
        :return PostComment object representing the unliked comment
        """
        response = self.sdk.api_client.delete(COMMENTS_API_ENDPOINT, comment_id, SIMPLE_LIKE_ENDPOINT)
        return PostComment(self.sdk, raw_data=response)

    def get_likes_for_post(self, post_id) -> List['PostLike']:
        """Retrieve the list of likes on post with ID `post_id`

        :param post_id: ID of the post whose likes to retrieve
        :return List of PostLike objects representing the individual Likes
        """
        response = self.sdk.api_client.get(POST_API_ENDPOINT, post_id, LIKES_ENDPOINT)
        return [PostLike(self.sdk, raw_data=like) for like in response]

    def get_likes_for_comment(self, comment_id) -> List['CommentLike']:
        """Retrieve the list of likes on comment with ID `comment_id`

        :param comment_id: ID of the comment whose likes to retrieve
        :return List of CommentLike objects representing the individual Likes
        """
        response = self.sdk.api_client.get(COMMENTS_API_ENDPOINT, comment_id, LIKES_ENDPOINT)
        return [CommentLike(self.sdk, raw_data=like) for like in response]

    def _commentify(self, comment_or_string):
        if isinstance(comment_or_string, str):
            return PostComment(self.sdk, text=comment_or_string)
        return comment_or_string

    def _postify(self, post_or_string):
        if isinstance(post_or_string, str):
            return Post(self.sdk, text=post_or_string)
        return post_or_string


class Stream:
    """Representation of a stream on Beekeeper"""
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data

    def get_id(self) -> str:
        """Returns the ID of this stream"""
        return self._raw.get('id')

    def get_description(self) -> str:
        """Returns the description of this stream"""
        return self._raw.get('description')

    def get_name(self) -> str:
        """Returns the name of this stream"""
        return self._raw.get('name')

    def post(self, post) -> 'Post':
        """Create a new post in this stream

        :param post: Post object representing the post to be created, or string containing post body.
        :return Post object representing the newly created post
        """
        self.sdk.streams.create_post(self.get_id(), post)

    def retrieve_posts(self, include_comments=False, before=None, limit=None) -> List['Post']:
        """Retrieve posts from this stream

        Retrieves the most recent `limit` posts that are older than `before`
        from this stream

        :param limit: Maximum number of posts to retrieve
        :param include_comments: Whether to include comments in the returned Post objects. Default False.
        :param before: Only posts created before this timestamp are returned.
        :return List of Post objects

        """
        return self.sdk.streams.get_posts_from_stream(
            self.get_id(),
            include_comments=include_comments,
            before=before,
            limit=limit
        )

    def retrieve_posts_iterator(self, include_comments=False) -> Iterator['Post']:
        """Retrieve posts from this stream

        Returns an iterator over posts in this stream, from newest to oldest.

        :param include_comments: Whether to include comments in the returned Post objects. Default False.
        :return Iterator of Post objects

        """
        return self.sdk.streams.get_posts_from_stream_iterator(
            self.get_id(),
            include_comments=include_comments,
        )


class Post:
    """Representation of a post inside a Stream"""
    def __init__(
            self,
            sdk,
            raw_data=None,
            text=None,
            title=None,
            labels=None,
            files=None,
            media=None,
            stream_id=None,
    ):
        """
        :param sdk: BeekeeperSDK
        :param raw_data: Raw API representation. Not required.
        :param text: Text of the post's body
        :param title: Title of the post
        :param labels: List of strings representing labels on this post
        :param files: List of FileData objects representing files attached to this post
        :param media: List of FileData objects representing media (pictures, videos) attached to this post
        :param stream_id: ID of the stream in which this post exists.
        """
        self.sdk = sdk
        self._raw = raw_data or {}
        if text:
            self._raw['text'] = text
        if title:
            self._raw['title'] = title
        if labels:
            self._raw['labels'] = labels
        if stream_id:
            self._raw['streamid'] = stream_id
        if files:
            self._raw['files'] = [file._raw for file in files]
        if media:
            self._raw['media'] = [medium._raw for medium in media]

    def get_id(self) -> str:
        return self._raw.get('id')

    def _timestamp(self):
        return self.get_created()

    def get_text(self) -> str:
        """Returns the text of this post's body"""
        return self._raw.get('text')

    def get_title(self) -> str:
        """Returns the title of this posts"""
        return self._raw.get('title')

    def get_labels(self) -> List[str]:
        """Returns the labels on this post as a list of strings"""
        return self._raw.get('labels')

    def get_display_name(self) -> str:
        """Returns the display name of this post's author"""
        return self._raw.get('display_name')

    def get_name(self) -> str:
        """Returns the name of this post's author"""
        return self._raw.get('name')

    def get_like_count(self) -> int:
        """Returns the number of likes on this post"""
        return self._raw.get('like_count')

    def get_display_name_extension(self) -> str:
        """Returns the display name extension of this post's author"""
        return self._raw.get('display_name_extension')

    def get_stream_id(self) -> int:
        """Returns the ID of the stream this post resides in"""
        return self._raw.get('streamid')

    def get_user_id(self) -> str:
        """Returns the user ID of this post's author"""
        return self._raw.get('user_id')

    def get_mentions(self) -> List[str]:
        """Returns a list of strings containing the user names of users who are mentioned in this post"""
        return self._raw.get('mentions')

    def get_created(self) -> str:
        """Returns the timestamp at which this post was created"""
        return self._raw.get('created')

    def get_avatar(self) -> str:
        """Returns the avatar URL of this post's author"""
        return self._raw.get('avatar')

    def get_profile(self) -> str:
        """Returns the user name of this post's author"""
        return self._raw.get('profile')

    def get_firstname(self) -> str:
        """Returns the first name of this post's author"""
        return self._raw.get('firstname')

    def get_files(self) -> List['FileData']:
        """Returns a list of FileData objects representing the files attached to this post"""
        return [FileData(self.sdk, raw_data=file) for file in self._raw.get('files', [])]

    def get_media(self) -> List['FileData']:
        """Returns a list of FileData objects representing the media (images, videos) attached to this post"""
        return [FileData(self.sdk, raw_data=file) for file in self._raw.get('media', [])]

    def like(self):
        """Likes this post"""
        return self.sdk.streams.like_post(self.get_id())

    def unlike(self):
        """Unlikes this post"""
        return self.sdk.streams.unlike_post(self.get_id())

    def comment(self, comment) -> 'PostComment':
        """Creates a comment on this post
        :param comment: PostComment representing the comment to create, or string
        :return PostComment object representing the newly created comment
        """
        return self.sdk.streams.comment_on_post(self.get_id(), comment)

    def delete(self):
        """Deletes this post"""
        return self.sdk.streams.delete_post(self.get_id())

    def retrieve_comments(self, before=None, limit=None) -> List['PostComment']:
        """Retrieve the newest `limit` comments older than `before` of this post

        :param limit: Maximum number of comments to retreive
        :param before: Only comments older than this timestamp are returned
        :return List of PostComment objects
        """
        return self.sdk.streams.get_post_comments(
            self.get_id(),
            before=before,
            limit=limit
        )

    def retrieve_comments_iterator(self) -> Iterator['PostComment']:
        """Retrieve iterator over comments of this post

        :return Iterator of PostComment objects, from newest to oldest
        """
        return self.sdk.streams.get_post_comments_iterator(
            self.get_id()
        )


class PostComment:
    """Representation of a comment on a Post"""
    def __init__(self, sdk, raw_data=None, text=None):
        """
        :param sdk: BeekeeperSDK
        :param raw_data: Raw API representation. Not required.
        :param text: Text of the comment
        """
        self.sdk = sdk
        self._raw = raw_data or {}
        if text:
            self._raw['text'] = text

    def get_id(self) -> int:
        """Returns the ID of this comment"""
        return self._raw.get('id')

    def _timestamp(self):
        return self.get_created()

    def get_post_id(self) -> int:
        """Returns the ID of the post this comment belongs to"""
        return self._raw.get('postid')

    def get_text(self) -> str:
        """Returns the text of this comment"""
        return self._raw.get('text')

    def get_display_name(self) -> str:
        """Returns the display name of this comment's author"""
        return self._raw.get('display_name')

    def get_name(self) -> str:
        """Returns the name of this comment's author"""
        return self._raw.get('name')

    def get_profile(self) -> str:
        """Returns the username of this comment's author"""
        return self._raw.get('profile')

    def get_like_count(self) -> int:
        """Returns the number of likes on this comment"""
        return self._raw.get('like_count')

    def get_display_name_extension(self) -> str:
        """Returns the display name extension of this comment's author"""
        return self._raw.get('display_name_extension')

    def get_mentions(self) -> List[str]:
        """Returns a list of strings containing the usernames of users mentioned in this comment"""
        return self._raw.get('mentions')

    def get_created(self) -> str:
        """Returns the timestamp at which this comment was created"""
        return self._raw.get('created')

    def get_user_id(self) -> str:
        """Returns the user ID of this comment's author"""
        return self._raw.get('user_id')

    def get_avatar(self) -> str:
        """Returns the avatar URL of this comment's author's avatar"""
        return self._raw.get('avatar')

    def like(self) -> 'PostComment':
        """Likes this comment
        :return PostComment object representing the liked comment"""
        return self.sdk.streams.like_comment(self.get_id())

    def unlike(self) -> 'PostComment':
        """Unlikes this comment
        :return PostComment object representing the unliked comment"""
        return self.sdk.streams.unlike_comment(self.get_id())

    def reply(self, comment) -> 'PostComment':
        """Creates a new comment on the same post as this comment
        :param comment: PostComment representing the comment to create, or string
        :return PostComment object representing the newly created comment
        """
        return self.sdk.streams.comment_on_post(self.get_post_id(), comment)

    def delete(self):
        """Deletes this comment"""
        return self.sdk.streams.delete_comment(self.get_id())


class PostLike:
    """Represent a specific like on a post"""
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_user_id(self) -> str:
        """Returns the ID of the user who liked the post"""
        return self._raw.get('user_id')

    def get_name(self) -> str:
        """Returns the name of the user who liked the post"""
        return self._raw.get('name')

    def get_display_name_extension(self) -> str:
        """Returns the display name extension of the user who liked the post"""
        return self._raw.get('display_name_extension')

    def get_profile(self) -> str:
        """Returns the username of the user who liked the post"""
        return self._raw.get('profile')

    def get_avatar(self) -> str:
        """Returns the avatar URL of the user who liked the post"""
        return self._raw.get('avatar')


class CommentLike:
    """Represent a specific like on a comment"""
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_name(self) -> str:
        """Returns the name of the user who liked the comment"""
        return self._raw.get('name')

    def get_display_name(self) -> str:
        """Returns the display name of the user who liked the comment"""
        return self._raw.get('display_name')

    def get_display_name_extension(self) -> str:
        """Returns the display name extension of the user who liked the comment"""
        return self._raw.get('display_name_extension')

    def get_profile(self) -> str:
        """Returns the username of the user who liked the comment"""
        return self._raw.get('profile')

    def get_avatar(self) -> str:
        """Returns the avatar URL of the user who liked the comment"""
        return self._raw.get('avatar')

