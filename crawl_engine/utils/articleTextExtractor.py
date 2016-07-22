"""
Requirements:
    https://pypi.python.org/pypi/readability-lxml
    https://pypi.python.org/pypi/jusText
    https://pypi.python.org/pypi/guess_language-spirit
    https://pypi.python.org/pypi/langdetect
"""
from readability.readability import Document
import justext


def extractArticleText(html):
    try:
        import guess_language
        readable_html = Document(html).summary()
        lang_name = guess_language.guessLanguageName(readable_html)

        title = Document(html).short_title()
        paragraphs = justext.justext(readable_html, justext.get_stoplist(lang_name))

        article_paragraphs = []
        article_text = ''
        for paragraph in paragraphs:
            if not paragraph.is_boilerplate and not title.lower() in paragraph.text.lower():
                    article_paragraphs.append(paragraph.text)
                    article_text = '\n'.join(article_paragraphs)
        return article_text

    except:
        return ''


def extractArticleTitle(html):
    try:
        return Document(html).short_title()
    except:
        return ''