class BeekeeperApiLimitBeforeIterator:
    """
    Iterator which goes backwards through timestamped data, starting at the newest entry
    """
    def __init__(self, api_call, limit=20, response_is_reversed=False):
        self.api_call = api_call
        self.limit = limit
        self.cache = []
        self.before = None
        self.last_round = False
        self.response_is_reversed = response_is_reversed

    def __iter__(self):
        self.before = None
        self.cache = []
        self.last_round = False
        return self

    def __next__(self):
        if self.cache:
            if self.response_is_reversed:
                return self.cache.pop(-1)
            else:
                return self.cache.pop(0)
        else:
            if self.last_round:
                raise StopIteration
            self.cache = self.api_call(limit=self.limit, before=self.before)
            if self.cache:
                if len(self.cache) < self.limit:
                    self.last_round = True
                if self.response_is_reversed:
                    self.before = self.cache[0]._timestamp()
                else:
                    self.before = self.cache[-1]._timestamp()
                if self.response_is_reversed:
                    return self.cache.pop(-1)
                else:
                    return self.cache.pop(0)
            else:
                raise StopIteration


class BeekeeperApiLimitOffsetIterator:
    """
    Iterator which goes through ordered data, starting at the first entry
    """
    def __init__(self, api_call, limit=20):
        self.api_call = api_call
        self.limit = limit
        self.cache = []
        self.offset = 0
        self.last_round = False

    def __iter__(self):
        self.offset = 0
        self.cache = []
        self.last_round = False
        return self

    def __next__(self):
        if self.cache:
            return self.cache.pop(0)
        else:
            if self.last_round:
                raise StopIteration
            self.cache = self.api_call(limit=self.limit, offset=self.offset)
            if self.cache:
                if len(self.cache) < self.limit:
                    self.last_round = True
                self.offset += len(self.cache)
                return self.cache.pop(0)
            else:
                raise StopIteration


class BeekeeperApiLimitAfterIterator:
    """
    Iterator which goes forward through timestamped data, starting at the oldest entry
    """
    def __init__(self, api_call, limit=20, response_is_reversed=False):
        self.api_call = api_call
        self.limit = limit
        self.cache = []
        self.after = "1999-02-12T11:22:28"
        self.last_round = False
        self.response_is_reversed = response_is_reversed

    def __iter__(self):
        self.after = "1999-02-12T11:22:28"
        self.cache = []
        self.last_round = False
        return self

    def __next__(self):
        if self.cache:
            if self.response_is_reversed:
                return self.cache.pop(0)
            else:
                return self.cache.pop(-1)
        else:
            if self.last_round:
                raise StopIteration
            self.cache = self.api_call(limit=self.limit, after=self.after)
            if self.cache:
                if len(self.cache) < self.limit:
                    self.last_round = True
                if self.response_is_reversed:
                    self.after = self.cache[-1]._timestamp()
                    return self.cache.pop(0)
                else:
                    self.after = self.cache[0]._timestamp()
                    return self.cache.pop(-1)
            else:
                raise StopIteration
