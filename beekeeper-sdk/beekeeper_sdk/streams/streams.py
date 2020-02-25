from beekeeper_sdk.files import FileData

STREAM_API_ENDPOINT = "streams"
POST_API_ENDPOINT = "posts"
COMMENTS_API_ENDPOINT = "comments"

COMMENTS_ENDPOINT = "comments"
POSTS_ENDPOINT = "posts"
SIMPLE_LIKE_ENDPOINT = "like"
LIKES_ENDPOINT = "likes"


class StreamApi:

    def __init__(self, sdk):
        self.sdk = sdk

    def get_streams(self):
        response = self.sdk.api_client.get(STREAM_API_ENDPOINT)
        return [Stream(self.sdk, raw_data=stream) for stream in response]

    def get_stream(self, stream_id):
        response = self.sdk.api_client.get(STREAM_API_ENDPOINT, stream_id)
        return Stream(self.sdk, raw_data=response)

    def get_posts_from_stream(self, stream_id, after=None, limit=None, include_comments=False, before=None):
        query = {}
        if limit:
            query["limit"] = limit
        if before is not None:
            query["before"] = before
        if after is not None:
            query["after"] = after
        query["include_comments"] = include_comments
        response = self.sdk.api_client.get(STREAM_API_ENDPOINT, stream_id, POSTS_ENDPOINT, query=query)
        return [Post(self.sdk, raw_data=post) for post in response]

    def get_post(self, post_id):
        response = self.sdk.api_client.get(POST_API_ENDPOINT, post_id)
        return Post(self.sdk, raw_data=response)

    def delete_post(self, post_id):
        response = self.sdk.api_client.delete(POST_API_ENDPOINT, post_id)
        return response.get("status") == "OK"

    def create_post(self, stream_id, post):
        real_post = self._postify(post)
        response = self.sdk.api_client.post(STREAM_API_ENDPOINT, stream_id, POSTS_ENDPOINT,
                                 payload=real_post._raw)
        return Post(self.sdk, raw_data=response)

    def get_post_comments(self, post_id):
        response = self.sdk.api_client.get(POST_API_ENDPOINT, post_id, COMMENTS_ENDPOINT)
        return [PostComment(self.sdk, raw_data=comment) for comment in response]

    def comment_on_post(self, post_id, comment):
        real_comment = self._commentify(comment)
        response = self.sdk.api_client.post(POST_API_ENDPOINT, post_id, COMMENTS_ENDPOINT,
                                 payload=real_comment._raw)
        return PostComment(self.sdk, raw_data=response)

    def delete_comment(self, comment_id):
        response = self.sdk.api_client.delete(COMMENTS_API_ENDPOINT, comment_id)
        return response.get("status") == "OK"

    def like_post(self, post_id):
        response = self.sdk.api_client.post(POST_API_ENDPOINT, post_id, SIMPLE_LIKE_ENDPOINT)
        return Post(self.sdk, raw_data=response)

    def unlike_post(self, post_id):
        response = self.sdk.api_client.delete(POST_API_ENDPOINT, post_id, SIMPLE_LIKE_ENDPOINT)
        return Post(self.sdk, raw_data=response)

    def like_comment(self, comment_id):
        response = self.sdk.api_client.post(COMMENTS_API_ENDPOINT, comment_id, SIMPLE_LIKE_ENDPOINT)
        return PostComment(self.sdk, raw_data=response)

    def unlike_comment(self, comment_id):
        response = self.sdk.api_client.delete(COMMENTS_API_ENDPOINT, comment_id, SIMPLE_LIKE_ENDPOINT)
        return PostComment(self.sdk, raw_data=response)

    def get_likes_for_post(self, post_id):
        response = self.sdk.api_client.get(POST_API_ENDPOINT, post_id, LIKES_ENDPOINT)
        return [PostLike(self.sdk, raw_data=like) for like in response]

    def get_likes_for_comment(self, comment_id):
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
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data

    def get_id(self):
        return self._raw.get("id")

    def get_description(self):
        return self._raw.get("description")

    def get_name(self):
        return self._raw.get("name")

    def post(self, post):
        self.sdk.streams.create_post(self.get_id(), post)


class Post:
    def __init__(self, sdk, raw_data=None,
                 text=None,
                 title=None,
                 labels=None,
                 files=None,
                 media=None,
                 streamid=None,
                 ):
        self.sdk = sdk
        self._raw = raw_data or {}
        if text:
            self._raw["text"] = text
        if title:
            self._raw["title"] = title
        if labels:
            self._raw["labels"] = labels
        if streamid:
            self._raw["streamid"] = streamid
        if files:
            self._raw["files"] = [file._raw for file in files]
        if media:
            self._raw["media"] = [medium._raw for medium in media]

    def get_id(self):
        return self._raw.get("id")

    def get_text(self):
        return self._raw.get("text")

    def get_title(self):
        return self._raw.get("title")

    def get_labels(self):
        return self._raw.get("labels")

    def get_display_name(self):
        return self._raw.get("display_name")

    def get_name(self):
        return self._raw.get("name")

    def get_like_count(self):
        return self._raw.get("like_count")

    def get_display_name_extension(self):
        return self._raw.get("display_name_extension")

    def get_streamid(self):
        return self._raw.get("streamid")

    def get_user_id(self):
        return self._raw.get("user_id")

    def get_mentions(self):
        return self._raw.get("mentions")

    def get_created(self):
        return self._raw.get("created")

    def get_avatar(self):
        return self._raw.get("avatar")

    def get_profile(self):
        return self._raw.get("profile")

    def get_firstname(self):
        return self._raw.get("firstname")

    def get_files(self):
        return [FileData(self.sdk, raw_data=file) for file in self._raw.get("files", [])]

    def get_media(self):
        return [FileData(self.sdk, raw_data=file) for file in self._raw.get("media", [])]

    def like(self):
        return self.sdk.streams.like_post(self.get_id())

    def unlike(self):
        return self.sdk.streams.unlike_post(self.get_id())

    def comment(self, comment):
        return self.sdk.streams.comment_on_post(self.get_id(), comment)

    def delete(self):
        return self.sdk.streams.delete_post(self.get_id())


class PostComment:
    def __init__(self, sdk, raw_data=None,
                 text=None):
        self.sdk = sdk
        self._raw = raw_data or {}
        if text:
            self._raw["text"] = text

    def get_id(self):
        return self._raw.get("id")

    def get_postid(self):
        return self._raw.get("postid")

    def get_text(self):
        return self._raw.get("text")

    def get_display_name(self):
        return self._raw.get("display_name")

    def get_name(self):
        return self._raw.get("name")

    def get_profile(self):
        return self._raw.get("profile")

    def get_like_count(self):
        return self._raw.get("like_count")

    def get_display_name_extension(self):
        return self._raw.get("display_name_extension")

    def get_mentions(self):
        return self._raw.get("mentions")

    def get_user_id(self):
        return self._raw.get("user_id")

    def get_avatar(self):
        return self._raw.get("avatar")

    def like(self):
        return self.sdk.streams.like_comment(self.get_id())

    def unlike(self):
        return self.sdk.streams.unlike_comment(self.get_id())

    def reply(self, comment):
        return self.sdk.streams.comment_on_post(self.get_postid(), comment)

    def delete(self):
        return self.sdk.streams.delete_comment(self.get_id())


class PostLike:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_user_id(self):
        return self._raw.get("user_id")

    def get_name(self):
        return self._raw.get("name")

    def get_display_name_extension(self):
        return self._raw.get("display_name_extension")

    def get_profile(self):
        return self._raw.get("profile")

    def get_avatar(self):
        return self._raw.get("avatar")


class CommentLike:
    def __init__(self, sdk, raw_data=None):
        self.sdk = sdk
        self._raw = raw_data or {}

    def get_name(self):
        return self._raw.get("name")

    def get_display_name(self):
        return self._raw.get("display_name")

    def get_display_name_extension(self):
        return self._raw.get("display_name_extension")

    def get_profile(self):
        return self._raw.get("profile")

    def get_avatar(self):
        return self._raw.get("avatar")

