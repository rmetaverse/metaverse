# module : citation
# preprocessstring.py
# 
# get string from input
# preprocess the string by removing characters/numbers as defined by user
# 
# March 2012
# miewkeen

import nltk, string
import getopt, sys
from unicodedata import category
import re

def usage():
    print "preprocess string"
    print "Usage: preprocessString.py  [options...] string"
    print "    -c/--no of character to remove   Character: 4 (default is 4)"
    print "    -n/--remove numeric (yes or no)  Numeric: Yes (default is yes)"
    print "    -h/--help                        This help text"
    sys.exit(2) 
    
def processing(string2process,character=4,numeric="yes"):
    processedstring = ""    

    # Process in unicode
    if type(string2process)==str:
        try:
            # Convert ascii string to unicode
            string2process = string2process.decode('ascii')

        except:            
            # Convert utf-8 string to unicode
            string2process = string2process.decode('utf-8')

    elif type(string2process)==unicode:
        pass
    else:
        raise Exception, "string2process must be a str or unicode"
    
    text = ''.join( ch if category(ch)[0] != 'P' else ' ' for ch in string2process)            

    processedstring = ''.join(text)

    if numeric == 'yes': 
        text2 = nltk.regexp_tokenize(processedstring, pattern=r'\D+')
        processedstring = ' '.join(text2)

    #remove string which length is less than character
    #print "removing string with less than %d character" % int(character)
    text3 = nltk.word_tokenize(processedstring)
    text3 = [w for w in text3 if len(w) > int(character)]
    
    processedstring = ' '.join(text3)

    
    return processedstring


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:n:vh", ["character=", "numeric=", "verbose", "help"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
    
    character = "4"
    numeric = "yes"
    string2process = ""
    verbose = False	
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
        elif o in ("-n", "--numeric"):
            numeric = a
        elif o in ("-c", "--character"):
            character = a
        else:
            assert False, "unhandled option"

    if len(args) < 1:
        usage()
    string2process = args[0]    
    
    
    if verbose == True:
        print "verbose = %s" % str(verbose)
        print "remove numeric = %s" % str(numeric)
        print "character to remove = %s" % int(character)
        print "string to process = %s" % str(string2process)
    
    
    processedstring = processing(string2process,character,numeric)  
    print processedstring
    
