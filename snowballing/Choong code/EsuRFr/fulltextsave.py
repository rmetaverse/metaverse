# Citation
# fulltextsave.py
#
# saving full text
#
# miewkeen
# April 2013

import re
from urllib2 import Request, urlopen, HTTPError
from pyPdf import PdfFileWriter, PdfFileReader
from StringIO import StringIO

from journalSave import *

def wolterskluwer(url):
    code = 0
    wk_pattern = 'wkhealth.com'
    wk_re = re.compile(wk_pattern)
    wk_result = wk_re.search(url)
    
    if wk_result is not None:
        code = 1
    return code
        
def find_pdfs(alllinks):    
    pdflink = ""
    for link in alllinks:        
        if ispdf(link):
            pdflink = link
            break
    return pdflink
            
def ispdf(url):
    pdf_pattern = '.pdf'
    #pdf_pattern2 = '/pdf/'
    pdf_re = re.compile(pdf_pattern)
    #pdf_re2 = re.compile(pdf_pattern)
    result = pdf_re.search(url)
    #result2 = pdf_re2.search(url)
    if (result is not None):# or (result2 is not None):
        return True    
    else:
        return False
        
def fulltextsave(articles, idx, alllinks, location):
    from webpageSave import getDirectedURL
    from find_pmid import pmid_find, pmcid_find
    
    url = articles[idx].attrs['url']
    url2 = articles[idx].attrs['url_material']
    pdfflag = False
    if url[0] is not None :
        link = getDirectedURL(url[0])
        if ispdf(link):            
            pdfok = url2pdf(link, location) # save the pdf in folder
            if pdfok == 0:
                pdfflag = True
        else:
            pdfok = url2journalsave(link, location)
            if pdfok == 0:
                pdfflag = True
                
    if url2[0] is not None and not pdfflag:
        link2 = getDirectedURL(url2[0])
        pdfok = url2pdf(link2, location) # save the pdf in folder
        if pdfok == 0:
            pdfflag = True
        else:
            pdfok = url2journalsave(link2, location)
            if pdfok == 0:
                pdfflag = True
                            
    if len(alllinks)>1 and not pdfflag: 
        pdf_url = find_pdfs(alllinks) # from all version, tried to get pdf ...
        if len(pdf_url) > 0:
            pdfok = url2pdf(pdf_url, location)
            if pdfok == 0:
                pdfflag = True
    
    # if no pdf...try to save pdf/html fulltext
    if not pdfflag:
        for orilink in alllinks:
            alllink = getDirectedURL(orilink)
            pdfok = url2journalsave(alllink, location)
            if pdfok == 0:
                pdfflag = True
                break
            if not pdfflag:
                pdfok = url2parsepdf(alllink, location)
                if pdfok == 0:
                    pdfflag = True
                    break

    if not pdfflag:               
        print "*** No pdf found on GS ***"
        if url[0] is not None:
            link = getDirectedURL(url[0])
            print "*** saving html page ***"
            url2websave(link, location)
            pdfflag = True                        
        elif url2[0] is not None:
            link2 = getDirectedURL(url2[0])
            print "*** saving html page ***"
            url2websave(link2, location)  
            pdfflag = True
        elif len(alllinks)>1:
            for alllink in alllinks:
                if len(pmid_find(alllink))==0 and len(pmcid_find(alllink))==0:
                    print "*** saving html page ***"            
                    url2websave(alllinks, location) #just save the first link
                    pdfflag = True
                    break
            
    return pdfflag

def fulltextsaveMAS(links, location): #full text save for MAS
    from webpageSave import getDirectedURL
    from find_pmid import pmid_find, pmcid_find
    
    pdfflag = False
    for orilink in links:
    #if link is not None :
        link = getDirectedURL(orilink) 
        if ispdf(link):            
            pdfok = url2pdf(link, location) # save the pdf in folder
            if pdfok == 0:
                pdfflag = True
                break
                
     # if no pdf...try to save pdf/html fulltext
    for orilink in links:
        link = getDirectedURL(orilink) 
        if not pdfflag:
            pdfok = url2journalsave(link, location)
            if pdfok == 0:
                pdfflag = True
                break

        if not pdfflag:
            pdfok = url2parsepdf(link, location)
            if pdfok == 0:
                pdfflag = True
                break    
        
    if not pdfflag:
        for orilink in links:
            link = getDirectedURL(orilink)
            if len(pmid_find(link))==0 and len(pmcid_find(link))==0:
                ###new: not to save wolters kluwer link page###
                wkyes = wolterskluwer(link)
                if wkyes == 0:
                    print "*** saving html page ***"
                    url2websave(link, location)
                    pdfflag = True
                    break
            
    return pdfflag

if __name__ == "__main__":
    sys.exit(0)
    
