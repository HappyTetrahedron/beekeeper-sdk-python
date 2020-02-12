from beekeepersdk.files import FileData

POST_API_ENDPOINT = "posts"
COMMENTS_ENDPOINT = "comments"
SIMPLE_LIKE_ENDPOINT = "like"
LIKES_ENDPOINT = "likes"

COMMENTS_API_ENDPOINT = "comments"


def get_post(sdk, post_id):
    response = sdk.get(POST_API_ENDPOINT, post_id)
    return Post(raw_data=response)


def delete_post(sdk, post_id):
    response = sdk.delete(POST_API_ENDPOINT, post_id)
    return response.get("status") == "OK"


def create_post(sdk, stream_id, post):
    real_post = _postify(post)
    real_post._raw["streamid"] = stream_id
    response = sdk.post(POST_API_ENDPOINT,
                        payload=real_post._raw)
    return Post(raw_data=response)


def get_post_comments(sdk, post_id):
    response = sdk.get(POST_API_ENDPOINT, post_id, COMMENTS_ENDPOINT)
    return [PostComment(raw_data=comment) for comment in response]


def comment_on_post(sdk, post_id, comment):
    real_comment = _commentify(comment)
    response = sdk.post(POST_API_ENDPOINT, post_id, COMMENTS_ENDPOINT,
                        payload=real_comment._raw)
    return PostComment(raw_data=response)


def delete_comment(sdk, comment_id):
    response = sdk.delete(COMMENTS_API_ENDPOINT, comment_id)
    return response.get("status") == "OK"


def like_post(sdk, post_id):
    response = sdk.post(POST_API_ENDPOINT, post_id, SIMPLE_LIKE_ENDPOINT)
    return Post(response)


def unlike_post(sdk, post_id):
    response = sdk.delete(POST_API_ENDPOINT, post_id, SIMPLE_LIKE_ENDPOINT)
    return Post(response)


def like_comment(sdk, comment_id):
    response = sdk.post(COMMENTS_API_ENDPOINT, comment_id, SIMPLE_LIKE_ENDPOINT)
    return PostComment(response)


def unlike_comment(sdk, comment_id):
    response = sdk.delete(COMMENTS_API_ENDPOINT, comment_id, SIMPLE_LIKE_ENDPOINT)
    return PostComment(response)


def get_likes_for_post(sdk, post_id):
    response = sdk.get(POST_API_ENDPOINT, post_id, LIKES_ENDPOINT)
    return [PostLike(raw_data=like) for like in response]


def get_likes_for_comment(sdk, comment_id):
    response = sdk.get(COMMENTS_API_ENDPOINT, comment_id, LIKES_ENDPOINT)
    return [CommentLike(raw_data=like) for like in response]


def _commentify(comment_or_string):
    if isinstance(comment_or_string, str):
        return PostComment(text=comment_or_string)
    return comment_or_string


def _postify(post_or_string):
    if isinstance(post_or_string, str):
        return Post(text=post_or_string)
    return post_or_string


class Post:
    def __init__(self, raw_data=None,
                 text=None,
                 title=None,
                 labels=None,
                 files=None,
                 media=None,
                 streamid=None,
                 ):
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
        return [FileData(raw_data=file) for file in self._raw.get("files", [])]

    def get_media(self):
        return [FileData(raw_data=file) for file in self._raw.get("media", [])]

    def like(self, sdk):
        return like_post(sdk, self.get_id())

    def unlike(self, sdk):
        return unlike_post(sdk, self.get_id())

    def comment(self, sdk, comment):
        return comment_on_post(sdk, self.get_id(), comment)

    def delete(self, sdk):
        return delete_post(sdk, self.get_id())


class PostComment:
    def __init__(self, raw_data=None,
                 text=None):
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

    def like(self, sdk):
        return like_comment(sdk, self.get_id())

    def unlike(self, sdk):
        return unlike_comment(sdk, self.get_id())

    def reply(self, sdk, comment):
        return comment_on_post(sdk, self.get_postid(), comment)

    def delete(self, sdk):
        return delete_comment(sdk, self.get_id())


class PostLike:
    def __init__(self, raw_data=None):
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
    def __init__(self, raw_data=None):
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

