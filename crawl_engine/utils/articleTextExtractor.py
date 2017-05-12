from readability.readability import Document


def extractArticleTitle(html):
    try:
        return Document(html).short_title()
    except:
        return ''
