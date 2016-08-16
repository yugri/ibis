def separate(str1, threshold=1000):
    out_list = []                 # List of output
    list1 = str1.strip().split()          # We split string into list of words
    temp_begin = 0                # The beginning of cut of sentences
    temp_end = 0                  # The end of last word of sequence
    temp_len = 0                  # Summary length of words
    new_end = 0                   # The end of last sentence(summary length is not higher than threshold)
    for i in list1:
        temp_end += 1
        if temp_len + len(i) < threshold:
            temp_len += len(i)
            if i[-1] == '.' or i[-1] == '?' or i[-1] == '!':
                new_end = temp_end
        else:
            print(temp_len)
            temp_len = 0
            out_list.append(list1[temp_begin:new_end])
            temp_begin = new_end
    else:
        out_list.append(list1[temp_begin:])
    return out_list