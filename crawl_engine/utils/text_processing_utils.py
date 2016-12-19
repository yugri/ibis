import re
import redis
from datetime import datetime, timedelta


def separate(str1, threshold=1000):
    """
    This method helps to separate the text before translation in Google Translate API.
    Translate API has default limits for translation and language detection and we tune our
    functionality to send by 1000 chars/sec.
    Details: https://cloud.google.com/translate/v2/pricing
    :param str1: str
    :param threshold: int
    :return: out_list: list
    """
    out_list = []                 # List of output
    list2 = []
    list1 = str1.strip().split()  # We split string into list of words
    for i in list1:
        if i[-1] == '.':
            list2.append(i)
        else:
            j = i+' '
            list2.append(j)
    j = ''
    list1 = []
    for i in list2:
        j = j+i
        if i[-1] == '.' or i[-1] == '?' or i[-1] == '!'or i[-2:] == '."' or i[-2:] == '?"' or i[-2:] == '!"':
            list1.append(j)
            j = ''
    list1.append(j)
    j = ''
    # print(list1)
    for i in list1:
        if len(j+i+' ') < threshold:
            j = j + i + ' '
        else:
            # print(len(j))        # If you want, you can watch length every group of sentences
            out_list.append(j)
            j = i + ' '
    else:
        out_list.append(j)
        j=''
    return out_list


def untag(text):
    return re.sub(r'<[^>]*>', '', text)


def split_by_sentences(text, num_sentences=10):
    """
    This function splits the text to the groups that consist of num_sentences sentences.
    The split function is based on regular expression.
    :param text: The text to be split
    :param num_sentences: Number of sentences in every part of list
    """
    # Here the newline symbols are deleted and replaced by the space
    text = re.sub('\n', ' ', text)
    text = re.sub('”|“', '"', text)
    # Here the text is splitted by sentences and later it is grouped into groups each with num_sentences sentences
    splitted_text = [sen + text[text.find(sen) + len(sen):text.find(sen) + len(sen)+2]
                     if text[text.find(sen) + len(sen): text.find(sen) + len(sen)+2].endswith(' ')
                     # This check is used to know is the element after dot a space or not
                     else sen + text[text.find(sen) + len(sen):text.find(sen) + len(sen)+2]
                     if len(sen) > 0  # last element of split is usually an empty string, so we ned to exclude it
                     else ''  #
                     for sen in re.split(re.compile(r'[.!?]+[\t ")]'), text)  # splitting text by sentences
                     ]
    return [''.join(splitted_text[n:n+num_sentences])
            for n in range(len(splitted_text)) if n % num_sentences == 0]


def tag_p(splitted_text):
    """
    This function adds <p> </p> tags to the text that was previously splitted by sentences.
    :param splitted_text:
    :return: String with parts of texts, separated by the <p> tag
    """
    def add_symbols(text_list):
        for num in range(len(text_list)):
            if len(re.findall('"', text_list[num])) % 2 == 1:
                if re.split(r'"[^"]*"', text_list[num])[-1][-1] != '"':
                    text_list[num] += '"'
                    if num != len(text_list) - 1:
                        text_list[num + 1] = '"' + text_list[num + 1]
        return splitted_text
    sent_list = add_symbols(splitted_text)
    return '\n'.join('<p> ' + sens + '</p>' for sens in sent_list)
