# module: citation
# find_bestresultMAS.py
# extracting reference section from file (text, pdf, doc)
#
# April 2013
# miewkeen


import string
import re
import sys
import preprocess_string

#only use "substring" and "wordorder"

def best_result_substring(compare_string,articles,preprocess=True,character=4,numeric="yes"):
    """test if 'title' is substring of compare_string
    may return empty result"""
    s_standard = compare_string.lower().replace(' ' ,'')
    result = []
    idx = 1000
    #for article in articles:
    #    s_comparing = article['title']
    for (idx, art) in enumerate(articles):
        #*MAS*#article = sorted(art.attrs.values(), key=lambda item:item[2])
        #*MAS*#s_comparing = article[0][0].lower() #getting the "Title"
        s_comparing = art.lower() #*MAS*#
        #print article
        #print s_comparing
        if s_comparing[0] == "[":            
            s_comparing = ' ' .join(string.split(s_comparing)[1:])            
        if preprocess:
            s_comparing = preprocess_string.processing(s_comparing,character,numeric)
        if s_comparing.lower().replace(' ' ,'') in s_standard:
            result = art#*MAS*#article
            break
    return result, idx


def best_result_wordorder(compare_string,articles,preprocess=True,character=4,numeric="yes"):
    """test if 'title' is a regex of compare_string
    (test wordhit in order)    
    may return empty result"""
    s_standard = compare_string.lower().replace(' ' ,'')
    result = []
    idx = 1000

    for (idx, art) in enumerate(articles):
        s_title = art.lower() #*MAS*#
        if s_title[0] == "[":    
            s_title = ' ' .join(string.split(s_title)[1:])
        if preprocess:
            s_title = preprocess_string.processing(s_title,character,numeric)
        token = re.findall('\w+', s_title.lower())
        s_comparing = '\w*' + '\w*'.join(token) + '\w*'
        if re.compile(s_comparing).match(s_standard) != None:
            result = art#*MAS*#article
            break
    return result, idx

        
if __name__ == "__main__":    

    sys.exit(0)
