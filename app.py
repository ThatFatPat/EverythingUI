from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from api import Item, ItemType, fetch_dir, fetch_search
from humanfriendly import format_size
import requests
import urllib

app = Flask('app')


@app.route('/favicon.ico')
def favicon():
    return '', 404


@app.route('/search')
def search():
    keyword = request.args.get('keyword')
    if not keyword:
        return 'No Keyword!', 400
    files = fetch_search(keyword)
    for file in files:
        file.link = '#' + file.name
    return render_template('index.html', **locals()), 200


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    files = fetch_dir(path)
    for file in files:
        file.size = format_size(file.size, binary=True)
        if file.typ is ItemType.FOLDER:
            file.link = urllib.parse.quote(
                path) + '/' + urllib.parse.quote(file.name)
            if not file.link.startswith('/'):
                file.link = '/' + file.link
        else:
            file.link = '#' + file.name
    return render_template('index.html', **locals()), 200
