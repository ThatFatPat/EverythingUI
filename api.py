from dataclasses import dataclass
from datetime import datetime, timedelta
import struct
from enum import Enum
from re import L
import urllib
import requests
import json

EVERYHING_URL = 'http://10.211.55.4:8080/'
USER = 'user'
PASSWORD = 'user'


class ItemType(Enum):
    FILE = 'file'
    FOLDER = 'folder'


@dataclass
class Item:
    typ: ItemType
    name: str
    size: int
    date: datetime
    link: str


@dataclass
class Result(Item):
    typ: ItemType
    path: str


def FILETIME_bytes_to_datetime(timestamp_int):
    us = timestamp_int // 10 - 11644473600000000
    return datetime(1970, 1, 1) + timedelta(microseconds=us)


# Raise 404 on real files, should be a download link
def fetch_dir(path):
    req = requests.get(urllib.parse.urljoin(EVERYHING_URL, urllib.parse.quote(path)),
                       auth=(USER, PASSWORD), params={'j': 1})
    req.raise_for_status()
    files = []
    for item in json.loads(req.text)['results']:
        files.append(Item(
            typ=ItemType(item['type']),
            name=item['name'],
            size=int(item['size']) if item['size'] else 0,
            date=FILETIME_bytes_to_datetime(int(item['date_modified'])),
            link=''
        ))
    return files


def fetch_search(keyword, offset=0, count=32):
    req = requests.get(EVERYHING_URL,
                       auth=(USER, PASSWORD),
                       params={
                           's': keyword,
                           'j': 1,
                           'offset': offset,
                           'count': count,
                           'path_column': 1,
                           'date_modified_column': 1,
                           'size_column': 1
                       })
    req.raise_for_status()
    results = []
    for item in json.loads(req.text)['results']:
        results.append(Result(
            typ=ItemType(item['type']),
            name=item['name'],
            size=int(item['size']) if item['size'] else 0,
            date=FILETIME_bytes_to_datetime(int(item['date_modified'])),
            path=item['path'],
            link=''
        ))
    return results
