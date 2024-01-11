#This file just to test out new functions before using them in the app
from thefuzz import fuzz, process

def find_max_fuzz_ratio_index(main_string, string_list):
    ratios = [fuzz.ratio(main_string, s) for s in string_list]
    max_index = ratios.index(max(ratios))
    return max_index

if __name__=="__main__":
    l=['Love by Drowning','The Robinsons']
    s = 'the robinson'
    print(fuzz.ratio(s1,s2))
