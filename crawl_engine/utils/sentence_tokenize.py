import re


def separate(str1, threshold=1000):
    out_list = []
    list1 = re.split(r'[!?.] ', str1)
    print(list1)
    temp_begin = 0
    temp_end = 0
    temp_len = 0
    for i in list1:
        temp_end += 1
        if temp_len + len(i) < threshold:
            temp_len += len(i)
        else:
            temp_len = 0
            out_list.append(list1[temp_begin:temp_end])
            temp_begin = temp_end
    else:
        out_list.append(list1[temp_begin:])
    return out_list