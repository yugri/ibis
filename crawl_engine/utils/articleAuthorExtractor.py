import re
import json
from bs4 import BeautifulSoup


def _extractFromLDJson(parsedHTML):
    author = ''
    script = parsedHTML.find('script', type='application/ld+json')
    if script:
        data = json.loads(script.text)
        try:
            author = data['author']['name']
        except Exception:
            pass
    return author


def _extractFromHTML(parsedHTML):
    author = ''
    for meta in parsedHTML.findAll('meta'):
        metaName = meta.get('name', '').lower()

        if 'author' == metaName:
            author = meta['content'].strip()
            break

        if 'blogger_name' == metaName:
            author = meta['content'].strip()
            break

    for tag in parsedHTML.find_all(itemprop='author'):
        author = tag.text.strip() if tag.text.strip() != '' else tag.get("content")

    for tag in parsedHTML.find_all('a', {'rel': 'author'}):
        author = tag.text.strip()

    for tag in parsedHTML.find_all(class_=re.compile('art-author', re.IGNORECASE)):
        author = tag.text.strip()

    return author


def extractArticleAuthor(html):

    articleAuthor = ''
    parsedHTML = BeautifulSoup(html, "lxml")
    author = _extractFromLDJson(parsedHTML)
    if author:
        articleAuthor = author
    author = _extractFromHTML(parsedHTML)
    if author:
        articleAuthor = author

    return articleAuthor
