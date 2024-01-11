def replace_words_in_string(input_string, list1, list2):
    result = []
    i = 0
    while i < len(input_string):
        if input_string[i] == "'":
            # Find the end of the quoted substring
            end_quote_index = input_string.find("'", i + 1)
            if end_quote_index != -1:
                quoted_substring = input_string[i + 1 : end_quote_index]
                if quoted_substring in list1:
                    index = list1.index(quoted_substring)
                    result.append("'" + list2[index] + "'")
                else:
                    result.append("'" + quoted_substring + "'")
                i = end_quote_index + 1
                continue
        result.append(input_string[i])
        i += 1

    output_string = ''.join(result)
    return output_string

if __name__=="__main__":
    s = "my name is 'maria'"
    l1 = ["my","maria"]
    l2 = ["your","Marie"]
    res = replace_words_in_string(s,l1,l2)
    print(res)