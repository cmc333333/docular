import json
from pathlib import PurePosixPath
from typing import NamedTuple
from urllib.parse import ParseResult, urlparse, urlunparse

import requests


class Api(NamedTuple):
    url: ParseResult

    @classmethod
    def new(cls, url: str):
        return cls(urlparse(url))

    def json(self):
        if self.url.scheme in ('', 'file'):
            with open(self.url.path, 'rb') as json_file:
                return json.load(json_file)
        else:
            return requests.get(urlunparse(self.url)).json()

    def __truediv__(self, path: str):
        new_path = PurePosixPath(self.url.path) / path
        return self.__class__(self.url._replace(path=str(new_path)))
