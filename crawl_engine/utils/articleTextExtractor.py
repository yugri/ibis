"""
Requirements:
    https://pypi.python.org/pypi/readability-lxml
    https://pypi.python.org/pypi/jusText
    https://pypi.python.org/pypi/guess_language-spirit
    https://pypi.python.org/pypi/langdetect
"""
from readability.readability import Document
import urllib
import justext
from langdetect import detect


def _someTestGuessLanguageModule():
    """
    Є деяка нестиковка мов в модулях. Деякі мови просто по різному названі.
    """
    langdetect_full_name = {'cs': 'Czech', 'mk': 'Macedonian', 'so': 'Somali', 'et': 'Estonian', 'sv': 'Swedish',
                            'cy': 'Welsh', 'de': 'German', 'ja': 'Japanese', 'gu': 'Gujarati', 'tl': 'Tagalog',
                            'ro': 'Romanian', 'hr': 'Croatian', 'zh-cn': 'Chinese', 'no': 'Norwegian',
                            'zh-tw': 'Chinese', 'fr': 'French', 'en': 'English', 'bn': 'Bengali', 'fa': 'Farsi',
                            'id': 'Indonesian', 'da': 'Danish', 'hi': 'Hindi', 'lt': 'Lithuanian', 'ar': 'Arabic',
                            'lv': 'Latvian', 'vi': 'Vietnamese', 'af': 'Afrikaans', 'hu': 'Hungarian', 'he': 'Hebrew',
                            'tr': 'Turkish', 'ur': 'Urdu', 'el': 'Greek', 'pl': 'Polish', 'kn': 'Kannada',
                            'pt': 'Portuguese', 'sl': 'Slovene', 'te': 'Telugu', 'fi': 'Finnish', 'bg': 'Bulgarian',
                            'ru': 'Russian', 'nl': 'Dutch', 'sq': 'Albanian', 'es': 'Spanish', 'ca': 'Catalan',
                            'pa': 'Punjabi', 'it': 'Italian', 'sw': 'Swahili', 'mr': 'Marathi', 'th': 'Thai',
                            'sk': 'Slovak', 'ne': 'Nepali', 'uk': 'Ukrainian', 'ta': 'Tamil', 'ko': 'Korean',
                            'ml': 'Malayalam'}
    page_language = langdetect_full_name[detect('some text')]

    import guess_language
    lang_check = guess_language.guessLanguageName("Ces eaux regorgent de renégats et de voleurs.")
    print(lang_check)
    justext_all_supported_language = ['Afrikaans', 'Albanian', 'Arabic', 'Aragonese', 'Armenian', 'Aromanian', 'Asturian', 'Azerbaijani', 'Basque', 'Belarusian', 'Belarusian_Taraskievica', 'Bengali', 'Bishnupriya_Manipuri', 'Bosnian', 'Breton', 'Bulgarian', 'Catalan', 'Cebuano', 'Chuvash', 'Croatian', 'Czech', 'Danish', 'Dutch', 'English', 'Esperanto', 'Estonian', 'Finnish', 'French', 'Galician', 'Georgian', 'German', 'Greek', 'Gujarati', 'Haitian', 'Hebrew', 'Hindi', 'Hungarian', 'Icelandic', 'Ido', 'Igbo', 'Indonesian', 'Irish', 'Italian', 'Javanese', 'Kannada', 'Kazakh', 'Korean', 'Kurdish', 'Kyrgyz', 'Latin', 'Latvian', 'Lithuanian', 'Lombard', 'Low_Saxon', 'Luxembourgish', 'Macedonian', 'Malay', 'Malayalam', 'Maltese', 'Marathi', 'Neapolitan', 'Nepali', 'Newar', 'Norwegian_Bokmal', 'Norwegian_Nynorsk', 'Occitan', 'Persian', 'Piedmontese', 'Polish', 'Portuguese', 'Quechua', 'Romanian', 'Russian', 'Samogitian', 'Serbian', 'Serbo_Croatian', 'Sicilian', 'Simple_English', 'Slovak', 'Slovenian', 'Spanish', 'Sundanese', 'Swahili', 'Swedish', 'Tagalog', 'Tamil', 'Telugu', 'Turkish', 'Turkmen', 'Ukrainian', 'Urdu', 'Uzbek', 'Vietnamese', 'Volapuk', 'Walloon', 'Waray_Waray', 'Welsh', 'West_Frisian', 'Western_Panjabi', 'Yoruba']

    guess_all_supported_language = ['Abkhazian', 'Afrikaans', 'Albanian', 'Arabic', 'Armenian', 'Azeri', 'Basque', 'Bengali', 'Breton', 'Bulgarian', 'Byelorussian', 'Cambodian', 'Catalan', 'Cebuano', 'Chinese', 'Croatian', 'Czech', 'Danish', 'Dutch', 'English', 'Esperanto', 'Estonian', 'Faroese', 'Farsi', 'Finnish', 'French', 'Frisian', 'Galician', 'Georgian', 'German', 'Greek', 'Gujarati', 'Hausa', 'Hawaiian', 'Hebrew', 'Hindi', 'Hungarian', 'Icelandic', 'Indonesian', 'Italian', 'Japanese', 'Kazakh', 'Klingon', 'Korean', 'Kurdish', 'Kyrgyz', 'Latin', 'Latvian', 'Lithuanian', 'Macedonian', 'Malagasy', 'Malay', 'Malayalam', 'Marathi', 'Mongolian', 'Ndebele', 'Nepali', 'Norwegian', 'Nynorsk', 'Pashto', 'Polish', 'Portuguese', 'Portuguese (Brazil)', 'Portuguese (Portugal)', 'Punjabi', 'Romanian', 'Russian', 'Sanskrit', 'Scots Gaelic', 'Sepedi', 'Serbian', 'Serbo-Croatian', 'Setswana', 'Slovak', 'Slovene', 'Somali', 'Spanish', 'Swahili', 'Swedish', 'Tagalog', 'Tamil', 'Telugu', 'Thai', 'Tibetan', 'Traditional Chinese (Taiwan)', 'Tsonga', 'Turkish', 'Twi', 'Ukrainian', 'Urdu', 'Uzbek', 'Venda', 'Vietnamese', 'Welsh', 'Xhosa', 'Zulu']

    justext_lang = set(justext_all_supported_language)
    guess_lang = set(guess_all_supported_language)

    print(justext_all_supported_language)
    print(guess_all_supported_language)

    print(len(justext_lang & guess_lang))
#_someTestGuessLanguageModule()

def extractArticleText(html):
    try:
        import guess_language
        readable_html = Document(html).summary()
        lang_name = guess_language.guessLanguageName(readable_html)

        #print(lang_name)
        #print('###########')
        title = Document(html).short_title()
        #print(title)
        #print('###########')
        paragraphs = justext.justext(readable_html, justext.get_stoplist(lang_name))

        article_paragraphs = []
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
"""
url = 'https://translate.google.com.ua/translate?sl=en&tl=uk&js=y&prev=_t&hl=uk&ie=UTF-8&u=http%3A%2F%2Findianexpress.com%2Farticle%2Findia%2Findia-news-india%2Fmaharashtra-cabinet-expansion-didnt-demand-berth-or-indulge-in-blackmail-sena-chief-uddhav-thackeray-2901359%2F&edit-text=&act=url'
request = urllib.request.Request(url)
request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
html = urllib.request.urlopen(request).read()
print(get_article_text(html))
"""