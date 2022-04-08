from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests
from humanfriendly import parse_size, parse_date
from datetime import datetime
from enum import Enum
import click
import urllib
from dateutil import parser

URL = 'http://10.211.55.4:8080/'


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
    path: str


def parse(body, search=False):
    soup = BeautifulSoup(body, 'html.parser')
    rows = soup.find_all('tr', {'class': 'trdata1'}) + \
        soup.find_all('tr', {'class': 'trdata2'})
    files = []

    for row in rows:
        typ = ItemType(row.find('td')['class'][0])
        file_tag = row.find('a')
        name = file_tag.text
        link = urllib.parse.unquote(file_tag['href'])

        size = row.find('td', {'class': 'sizedata'}).text.replace(',', '')
        size = parse_size(size if size else '0', binary=True)

        date = parser.parse(row.find('td', {'class': 'modifieddata'}).text)

        if search:
            path = row.find('td', {'class': 'path'}).text
            files.append(Result(typ=typ, name=name, size=size,
                         date=date, link=link, path=path))
        else:
            files.append(Item(typ=typ, name=name, size=size,
                         date=date, link=link))

    return files


@click.command()
@click.argument('URI')
def main(uri):
    req = requests.get(url=urllib.parse.urljoin(
        URL, uri), auth=('user', 'user'))
    req.raise_for_status()
    print(parse(req.text))


if __name__ == '__main__':
    main()
