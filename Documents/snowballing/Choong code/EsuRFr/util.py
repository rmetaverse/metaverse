# Citation
# util.py
#
# Utilities support functions
#
# miewkeen
# April 2013


def find_bestMAS(compare_string, articles, preprocess=True, character=4, numeric="yes"):
    import find_bestresultMAS
    result, idx = find_bestresultMAS.best_result_substring(compare_string, articles, preprocess, character, numeric)
    if len(result) == 0:
        result, idx  = find_bestresultMAS.best_result_wordorder(compare_string, articles,preprocess, character, numeric)    
    return result, idx

def find_best(compare_string, articles, preprocess=True, character=4, numeric="yes"):
    import find_bestresult
    result, idx = find_bestresult.best_result_substring(compare_string, articles, preprocess, character, numeric)
    if len(result) == 0:
        result, idx  = find_bestresult.best_result_wordorder(compare_string, articles,preprocess, character, numeric)    
    return result, idx

def extract_references_refext2(filename, filetype):
    """extract references using parscit
    differences: use pdftotext as default"""
    import references
    import commands
    text = ""
    if filetype == "pdf":
        text = references.convert_pdf_to_text_pdftotext(filename)
    elif filetype == "doc":
        text = references.convert_doc_to_text_antiword(filename)        
    elif filetype == "docx":
        text = references.convert_doc_to_text_docx(filename)        
    elif filetype == "txt":
        text = references.convert_txt_to_text(filename)        
    elif filetype == "htm" or filetype == "html":       #new Apr 2013
        text = references.convert_html_to_text_nltk(filename)
    elif filetype == "http" or filetype == "https":     #new Apr 2013
        text = references.convert_http_to_text_nltk(filename)
        
    #print text
    tmpfile = references.write_tmpfile(text, encoding="utf-8")
    if tmpfile:
        try:
            parscitreflist = references.segment_rawstring_refext2(tmpfile)
            return parscitreflist            
        except:
            pass
        finally:
            # remove tmp file
            commands.getstatusoutput("rm %s" % tmpfile)
    else:
        print "Failed to write to tmpfile\n"


if __name__ == "__main__":
    sys.exit(0)
