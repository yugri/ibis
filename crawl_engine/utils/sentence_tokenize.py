def separate(str1, threshold=1000):
    """
    This method helps to separate the text before translation in Google Translate API.
    Translate API has default limits for translation and language detection and we tune our
    functionality to send by 1000 chars/sec.
    Details: https://cloud.google.com/translate/v2/pricing
    :param str1:
    :param threshold:
    :return:
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