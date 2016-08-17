import requests
import re
import json
import logging
from dateutil.parser import parse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parseStrDate(dateString):
    try:
        dateTimeObj = parse(dateString, fuzzy=True)
        return dateTimeObj
    except:
        return None


def _extractFromURL(url):

    #Regex by Newspaper3k  - https://github.com/codelucas/newspaper/blob/master/newspaper/urls.py
    m = re.search(r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?', url)
    if m:
        return parseStrDate(m.group(0))

    return None


def _extractFromLDJson(parsedHTML):
    jsonDate = None
    try:
        script = parsedHTML.find('script', type='application/ld+json')
        if script is None:
            return None

        data = json.loads(script.text)

        try:
            jsonDate = parseStrDate(data['dateCreated'])
        except Exception:
            pass

        try:
            jsonDate = parseStrDate(data['datePublished'])
        except Exception:
            pass

    except Exception:
        return None

    return jsonDate


def _extractFromMeta(parsedHTML):

    metaDate = None
    for meta in parsedHTML.findAll("meta"):
        metaName = meta.get('name', '').lower()
        itemProp = meta.get('itemprop', '').lower()
        httpEquiv = meta.get('http-equiv', '').lower()
        metaProperty = meta.get('property', '').lower()

        #<meta name="pubdate" content="2015-11-26T07:11:02Z" >
        if 'pubdate' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name='publishdate' content='201511261006'/>
        if 'publishdate' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="timestamp"  data-type="date" content="2015-11-25 22:40:25" />
        if 'timestamp' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="DC.date.issued" content="2015-11-26">
        if 'dc.date.issued' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta property="article:published_time"  content="2015-11-25" />
        if 'article:published_time' == metaProperty:
            metaDate = meta['content'].strip()
            break
            #<meta name="Date" content="2015-11-26" />
        if 'date' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta property="bt:pubDate" content="2015-11-26T00:10:33+00:00">
        if 'bt:pubdate' == metaProperty:
            metaDate = meta['content'].strip()
            break
            #<meta name="sailthru.date" content="2015-11-25T19:56:04+0000" />
        if 'sailthru.date' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="article.published" content="2015-11-26T11:53:00.000Z" />
        if 'article.published' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="published-date" content="2015-11-26T11:53:00.000Z" />
        if 'published-date' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="article.created" content="2015-11-26T11:53:00.000Z" />
        if 'article.created' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="article_date_original" content="Thursday, November 26, 2015,  6:42 AM" />
        if 'article_date_original' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="cXenseParse:recs:publishtime" content="2015-11-26T14:42Z"/>
        if 'cxenseparse:recs:publishtime' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="DATE_PUBLISHED" content="11/24/2015 01:05AM" />
        if 'date_published' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
        if 'datepublished' == itemProp:
            metaDate = meta['content'].strip()
            break

        #<meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
        if 'datecreated' == itemProp:
            metaDate = meta['content'].strip()
            break

        #<meta http-equiv="data" content="10:27:15 AM Thursday, November 26, 2015">
        if 'date' == httpEquiv:
            metaDate = meta['content'].strip()
            break

    if metaDate is not None:
        return parseStrDate(metaDate)

    return None


def _extractFromHTMLTag(parsedHTML):
    for time in parsedHTML.findAll("time"):
        datetime = time.get('datetime', '')
        if len(datetime) > 0:
            return parseStrDate(datetime)

        datetime = time.get('class', '')
        if len(datetime) > 0 and datetime[0].lower() == "timestamp":
            return parseStrDate(time.string)

    tag = parsedHTML.find("span", {"itemprop": "datePublished"})
    if tag is not None:
        dateText = tag.get("content")
        if dateText is None:
            dateText = tag.text
        if dateText is not None:
            return parseStrDate(dateText)

    for tag in parsedHTML.find_all(class_=re.compile("published|pubdate|timestamp|article_date|articledate|date",
                                                     re.IGNORECASE)):
        dateText = tag.string
        if dateText is None:
            dateText = tag.text

        possibleDate = parseStrDate(dateText)

        if possibleDate is not None:
            return possibleDate

    return None


def extractArticlePublishedDate(articleLink, html=None):

    # print("Extracting date from " + articleLink)
    logger.info("Extracting date from " + articleLink)

    articleDate = None

    try:
        articleDate = _extractFromURL(articleLink)

        if html is None:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/41.0.2228.0 Safari/537.36',
            }
            r = requests.get(articleLink, headers=headers)
            html = r.text
        parsedHTML = BeautifulSoup(html, "lxml")

        possibleDate = _extractFromLDJson(parsedHTML)
        if possibleDate is None:
            possibleDate = _extractFromMeta(parsedHTML)
        if possibleDate is None:
            possibleDate = _extractFromHTMLTag(parsedHTML)


        articleDate = possibleDate if possibleDate != None else ''

    except Exception as e:
        print("Exception in extractArticlePublishedDate for " + articleLink)
        print(e.message, e.args)

    return articleDate