def unpack(list1):
    list2 = []
    sum_str = ''
    for i in list1:
        sum_str = sum_str+i
        if i[-1] == '.':
                list2.append(sum_str)
    return list2


def separate(str1, threshold=1000):
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
        if j[-1] == '.' or j[-1] == '?' or j[-1] == '!':
            list1.append(j)
            j = ''
    j = ''
    for i in list1:
        if len(j+i+' ') < threshold:
            j = j + i + ' '
        else:
            # print(len(j))        # If you want, you can watch length every group of sentences
            out_list.append(j)
            j = i + ' '
    else:
        # print(len(j))
        out_list.append(j)
    return out_list