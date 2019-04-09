# module: citation
# reference_extraction.py
# extracting reference section from file (text, pdf, doc)
#
# miewkeen



""" Module: citation
    reference_extraction.py
    extracting reference section from file (text, pdf, doc) input
"""
import sys, os, subprocess, getopt
import nltk, string
import commands, json
import pyPdf
#docx.py can be downloaded from https://github.com/mikemaccana/python-docx/blob/master/docx.py
from docx import opendocx,getdocumenttext
from random import choice
import string
import codecs

def normalize_ligatures(data):
    # expecting data in unicode
    ligatures = {        
        0x0026: u'Et',
        0x0026: u'Et',
        0x00C6: u'AE',
        0x00E6: u'ae',
        0x0152: u'OE',
        0x0153: u'oe',
        0x0132: u'IJ',
        0x0133: u'ij',
        0x1D6B: u'ue',
        0xFB00: u'ff',
        0xFB01: u'fi',
        0xFB02: u'fl',
        0xFB03: u'ffi',
        0xFB04: u'ffl',        
        0xFB06: u'st',
    }
    return data.translate(ligatures)

def convert_http_to_text_nltk(http):
    """Convert http to text using nltk"""    
    import urllib2
    req = urllib2.Request(http,headers={'User-Agent' : "Magic Browser"})
    j = urllib2.urlopen(req)
    text = j.read()
    try:
        from feedparser import _getCharacterEncoding as enc
    except ImportError:
        enc = lambda x, y: ('utf-8', 1)
    encoding = enc(j.headers, text)[0]
    if encoding == 'us-ascii':
        encoding = 'utf-8'
    data = text.decode(encoding)
    output = nltk.clean_html(data)
    return normalize_ligatures(output.decode("utf-8")) #return unicode
    
    
def convert_html_to_text_nltk(html):
    """Convert a html file to text using nltk"""
    data = open(html, 'rb').read()
    try:
        from chardet import detect
    except ImportError:
        detect = lambda x: {'encoding': 'utf-8'}
    encoding = detect(data)['encoding']
    data = data.decode(encoding)
    output = nltk.clean_html(data)
    return normalize_ligatures(output.decode("utf-8")) #return unicode
    

def convert_pdf_to_text_pdftotext(pdf):
    """Convert a pdf file to text using pdftotext and return the text"""
    (status, output) = commands.getstatusoutput('pdftotext -raw -enc UTF-8 "%s" -' % pdf)
    
    # pdftotext doesn't handle ligatures process, therefore we translate them
    return normalize_ligatures(output.decode("utf-8")) #return unicode



# make sure the Resource files, e.g. UTF-8.txt is placed into ~/.antiword
def convert_doc_to_text_antiword(doc):
    """Convert a doc file to text and return the text"""
    (status, output) = commands.getstatusoutput("antiword %s" % doc)    
    return output.decode("utf-8") #return unicode


def convert_doc_to_text_docx(docx):
    """Convert a doc file to text and return the text"""
    document = opendocx(docx)
    paratextlist = getdocumenttext(document)
    output = '\n\n'.join(paratextlist)    
    return output #output already in unicode


def convert_txt_to_text(txt):
    f = open(txt)
    output = f.read()
    f.close()    
    return output.decode("utf-8") #return unicode


def segment_rawstring_refext2(textfile):
    """Segment individual ref strings using reference_extraction(Parscit)
    Input whole text file
    Return individual ref strings as lists
    """
    (status, output) = commands.getstatusoutput("perl preprocess_refext2.pl %s 2>/dev/null" % textfile)
    return json.loads(output) #json return unicode
    


# read file
# normalized to lowercase
# find the word "references" (should be the final "references" if many is found)
# whatever below we need to parse

def genrandomstring(length=8, chars=string.letters + string.digits):    
    return ''.join([choice(chars) for i in range(length)])

def remove_tmpfile(tmpfile):
    commands.getstatusoutput("rm %s" % tmpfile)
    
def write_tmpfile(buf,encoding="utf-8"):
    # expecting buf in unicode
    if encoding not in ("utf-8",):
        print "Unsupport encoding\n"
        return None
        
    tmpfile = genrandomstring()
    try:
        f = codecs.open(tmpfile, "w", encoding)
        f.write(buf)
        f.close()
        return tmpfile
    except:
        remove_tmpfile(tmpfile)
        return None

def write_tmpfile_txt(buf,encoding="utf-8"):
    # expecting buf in unicode
    if encoding not in ("utf-8",):
        print "Unsupport encoding\n"
        return None
        
    tmpfile = genrandomstring()
    tmpfile = tmpfile + ".txt"
    try:
        f = codecs.open(tmpfile, "w", encoding)
        f.write(buf)
        f.close()
        return tmpfile
    except:
        remove_tmpfile(tmpfile)
        return None


def usage():
    print "references extraction"
    print "Usage: references.py [options...] file"
    print "    -t/--type                file type (pdf, doc, docx and txt)"
    print "    -v/--verbose             verbose"
    print "    -h/--help                This help text"
    sys.exit(2)

    # python references.py -t word "testdata/testdata_refextraction.docx"
    # python references.py -t pdf "testdata/testdata_refextraction.pdf"


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:vh", ["type=", "verbose", "help"])
    except getopt.GetoptError, err:
        print str(err)
        usage()

    verbose = False
    filetype = None
    filename = None
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
        elif o in ("-t", "--type"):
            filetype = a
        else:
            assert False, "unhandled option"

    if filetype not in ["pdf", "doc", "docx", "txt"]:
        usage()

    if len(args) < 1:
        usage()
    filename = args[0]
    

    text = ""
    if filetype == "pdf":
        text = convert_pdf_to_text_pdftotext(filename)
    elif filetype == "doc":
        text = convert_doc_to_text_antiword(filename)        
    elif filetype == "docx":
        text = convert_doc_to_text_docx(filename)        
    elif filetype == "txt":
        text = convert_txt_to_text(filename)        

    
    #print text
    tmpfile = write_tmpfile(text)
    if tmpfile:
        try:
            parscitreflist = segment_rawstring_refext2(tmpfile)            
            print json.dumps(parscitreflist, ensure_ascii=False, indent=4)
        except:
            pass
        finally:
            pass
            # remove tmp file
            #commands.getstatusoutput("rm %s" % tmpfile)
            
    else:
        print "Failed to write to tmpfile\n"
        
    sys.exit(0)
    

